"""Official X API v2 adapter. Only fetch_latest can initiate outbound requests.

No polling, pagination, automatic retries, raw error persistence, or token logging.
The persisted request ledger and global cooldown apply across accounts/processes.
"""
from datetime import datetime, timezone
import json
import math
import os
import re
import time
from email.utils import parsedate_to_datetime

import httpx
from . import db

BASE_URL = 'https://api.x.com/2'
CACHE_SECONDS = 15 * 60
USER_CACHE_SECONDS = 7 * 24 * 60 * 60
COOLDOWN_SECONDS = 10 * 60
DAILY_REQUEST_CAP = 10
MESSAGES = {
    'missing_credentials': 'Add X_BEARER_TOKEN to your private server .env, then restart. No X request was made.',
    'disabled': 'Live fetching is off. With $0 credits, keep X_LIVE_ENABLED=false. Enable locally only after confirming X access and credits.',
    'ready': 'Ready for a manual fetch. X may charge for API reads; no request has been made by switching modes.',
    'cached': 'Using cached X posts. No new X request was made.',
    'success': 'Latest X response cached. Analyze these posts without another API request.',
    'empty': 'X returned no public posts. This is not demo data; no synthetic posts were substituted.',
    'authentication_error': 'X rejected authentication (401). Check or rotate your Bearer Token privately; do not paste it here.',
    'access_denied': 'X denied access (403). Verify your app permissions, API plan and endpoint access.',
    'insufficient_credits': 'X reported a payment or credit restriction. Check your X Developer billing and access; this app does not purchase credits.',
    'rate_limited': 'X rate limit reached (429). Wait until the retry time shown; automatic retry is off.',
    'cooldown': 'Refresh cooldown active. Use the cached posts or wait until the next allowed fetch.',
    'daily_cap': 'Daily request cap reached or insufficient request slots remain. Use the cache; budget resets at midnight UTC.',
    'network_error': 'Unable to reach X. Check your connection. No automatic retries or demo substitution occurred.',
    'service_error': 'X is temporarily unavailable. Cached posts are preserved; retry manually after the cooldown.',
    'account_not_found': 'X account not found (404). Check the username and whether the account is public.',
    'invalid_response': 'X returned incomplete or unexpected data. Existing cache is preserved; no fabricated values were added.',
    'request_rejected': 'X rejected the request. Confirm the account and current API endpoint access in the developer portal.',
}


class XError(Exception):
    def __init__(self, code, status=400, retry_at=None):
        self.code, self.status, self.retry_at = code, status, retry_at
        super().__init__(MESSAGES[code])


def client():
    # Redirects/retries remain disabled: never forward Authorization to another host.
    return httpx.Client(timeout=httpx.Timeout(15), follow_redirects=False)


def username(value):
    value = value.removeprefix('@').lower()
    if not re.fullmatch(r'[a-z0-9_]{1,15}', value):
        raise XError('request_rejected', 422)
    return value


def stamp(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat() if epoch else None


def _record(con, handle):
    row = con.execute('SELECT payload FROM x_accounts WHERE handle=?', (handle,)).fetchone()
    return json.loads(row['payload']) if row else {}


def _store(con, handle, value):
    con.execute('INSERT OR REPLACE INTO x_accounts VALUES(?,?)', (handle, json.dumps(value)))


def cached_posts(handle):
    with db.connect() as con:
        return [json.loads(r['payload']) for r in con.execute(
            'SELECT payload FROM x_posts WHERE handle=? ORDER BY created_at DESC', (handle,))]


def status(handle='elonmusk', now=None):
    handle = username(handle)
    now = time.time() if now is None else now
    day_start = int(now // 86400) * 86400
    configured = bool(os.environ.get('X_BEARER_TOKEN', '').strip())
    enabled = os.environ.get('X_LIVE_ENABLED', 'false').lower() == 'true'
    with db.connect() as con:
        record = _record(con, handle)
        control = con.execute('SELECT * FROM x_control WHERE id=1').fetchone()
        used = con.execute('SELECT count(*) FROM x_requests WHERE attempted_at>=?', (day_start,)).fetchone()[0]
        count = con.execute('SELECT count(*) FROM x_posts WHERE handle=?', (handle,)).fetchone()[0]
    retry = max(control['next_fetch_at'], control['blocked_until'])
    code = record.get('code', 'ready')
    needed = 1 if record.get('user_id') and now-record.get('resolved_at',0)<USER_CACHE_SECONDS else 2
    if code == 'daily_cap' and used+needed <= DAILY_REQUEST_CAP:
        code = 'cached' if record.get('last_fetch') else 'ready'
    if code == 'cooldown' and control['next_fetch_at'] <= now:
        code = 'cached' if record.get('last_fetch') else 'ready'
    if code == 'rate_limited' and control['blocked_until'] <= now:
        code = 'cached' if record.get('last_fetch') else 'ready'
    if code == 'daily_cap' or used >= DAILY_REQUEST_CAP:
        retry = max(retry, day_start+86400)
    if code in ('ready', 'success', 'empty', 'cached'):
        code = 'cached' if record.get('last_fetch') else 'ready'
    if not configured:
        code = 'missing_credentials'
    elif not enabled:
        code = 'disabled'
    return dict(username=handle, code=code, message=MESSAGES[code], credentials_configured=configured,
                live_enabled=enabled, last_fetch=stamp(record.get('last_fetch')),
                last_attempt=stamp(record.get('last_attempt')), last_retrieved=record.get('last_count', 0),
                cached_posts=count, cache_fresh=bool(record.get('last_fetch') and now-record['last_fetch']<CACHE_SECONDS),
                next_fetch_at=stamp(retry) if retry>now else None, requests_used=used,
                request_cap=DAILY_REQUEST_CAP, budget_resets_at=stamp(day_start+86400),
                cache_seconds=CACHE_SECONDS, cooldown_seconds=COOLDOWN_SECONDS,
                last_error=record.get('code') if record.get('code') not in (None,'success','empty','cached') else None)


def _claim(handle, now, required):
    """Atomically prevent concurrent refreshes and multi-account cooldown bypass."""
    with db.connect() as con:
        con.execute('BEGIN IMMEDIATE')
        control = con.execute('SELECT * FROM x_control WHERE id=1').fetchone()
        if control['blocked_until'] > now:
            raise XError('rate_limited', 429, control['blocked_until'])
        if control['next_fetch_at'] > now:
            raise XError('cooldown', 429, control['next_fetch_at'])
        day_start = int(now // 86400)*86400
        used = con.execute('SELECT count(*) FROM x_requests WHERE attempted_at>=?', (day_start,)).fetchone()[0]
        if used+required > DAILY_REQUEST_CAP:
            raise XError('daily_cap', 429, day_start+86400)
        con.execute('UPDATE x_control SET next_fetch_at=? WHERE id=1', (now+COOLDOWN_SECONDS,))
        record = _record(con, handle)
        record['last_attempt'] = now
        _store(con, handle, record)


def _retry_time(response, now):
    candidates = [now+15*60]  # conservative default if headers are absent/malformed
    try:
        value = float(response.headers.get('x-rate-limit-reset', 0))
        if math.isfinite(value) and 0 < value < 253402300799:
            candidates.append(value)
    except (ValueError, TypeError):
        pass
    raw = response.headers.get('retry-after', '0')
    try:
        value = now+float(raw)
    except ValueError:
        try:
            value = parsedate_to_datetime(raw).timestamp()
        except (ValueError, TypeError, OverflowError):
            value = now
    if math.isfinite(value) and 0 < value < 253402300799:
        candidates.append(value)
    return max(candidates)


def _get(session, path, token, params=None):
    now = time.time()
    with db.connect() as con:
        con.execute('BEGIN IMMEDIATE')
        control = con.execute('SELECT blocked_until FROM x_control WHERE id=1').fetchone()
        if control['blocked_until']>now:
            raise XError('rate_limited', 429, control['blocked_until'])
        day_start = int(now // 86400)*86400
        if con.execute('SELECT count(*) FROM x_requests WHERE attempted_at>=?', (day_start,)).fetchone()[0]>=DAILY_REQUEST_CAP:
            raise XError('daily_cap', 429, day_start+86400)
        # Count every attempt, including failures, before touching the network.
        con.execute('INSERT INTO x_requests(attempted_at) VALUES(?)', (now,))
    try:
        response = session.get(BASE_URL+path, headers={'Authorization': 'Bearer '+token}, params=params)
    except httpx.RequestError:
        raise XError('network_error', 502) from None
    if response.status_code >= 300:
        # Inspect only for classification. Never echo/store response text or headers.
        credit = any(x in response.text.lower() for x in ('creditsdepleted', 'insufficient credits', 'usagecapexceeded', 'payment required', 'insufficient balance'))
        code = ('insufficient_credits' if response.status_code==402 or (response.status_code==403 and credit) else
                {401:'authentication_error', 403:'access_denied', 404:'account_not_found', 429:'rate_limited'}.get(
                    response.status_code, 'service_error' if response.status_code>=500 else 'request_rejected'))
        retry = _retry_time(response, now) if code=='rate_limited' else None
        if retry:
            with db.connect() as con:
                con.execute('UPDATE x_control SET blocked_until=max(blocked_until,?) WHERE id=1', (retry,))
        raise XError(code, 429 if code=='rate_limited' else 502, retry)
    # If X reports the endpoint budget exhausted even on success, respect reset.
    if response.headers.get('x-rate-limit-remaining') == '0':
        with db.connect() as con:
            con.execute('UPDATE x_control SET blocked_until=max(blocked_until,?) WHERE id=1', (_retry_time(response, now),))
    try:
        payload = response.json()
    except ValueError:
        raise XError('invalid_response', 502) from None
    if not isinstance(payload, dict) or payload.get('errors'):
        raise XError('invalid_response', 502)
    return payload


def normalize_post(value, handle):
    """Missing engagement stays None; references distinguish replies/quotes/reposts."""
    if not isinstance(value, dict):
        raise ValueError('Invalid post')
    identifier = value.get('id')
    text = value.get('text')
    if not isinstance(identifier,str) or not identifier.isdigit() or not isinstance(text,str) or not text.strip():
        raise ValueError('Invalid post')
    created = datetime.fromisoformat(value['created_at'].replace('Z','+00:00'))
    if created.tzinfo is None:
        raise ValueError('Missing timezone')
    references = value.get('referenced_tweets', [])
    if not isinstance(references,list):
        raise ValueError('Invalid references')
    refs = []
    for item in references:
        if not isinstance(item,dict) or item.get('type') not in ('retweeted','quoted','replied_to') or not str(item.get('id','')).isdigit():
            raise ValueError('Invalid reference')
        refs.append({'type':item['type'], 'id':str(item['id'])})
    types = {r['type'] for r in refs}
    metrics = value.get('public_metrics') or {}
    if not isinstance(metrics,dict):
        raise ValueError('Invalid metrics')
    def metric(key):
        result = metrics.get(key)
        if result is not None and (type(result) is not int or result<0):
            raise ValueError('Invalid metric')
        return result
    return dict(id='x:'+identifier, x_id=identifier, handle=handle, text=text,
        created_at=created.astimezone(timezone.utc).isoformat(), url=f'https://x.com/{handle}/status/{identifier}',
        likes=metric('like_count'), reposts=metric('retweet_count'), replies=metric('reply_count'),
        quotes=metric('quote_count'), impressions=metric('impression_count'), bookmarks=metric('bookmark_count'),
        provenance='live_x', author_id=value.get('author_id'), post_type=('repost' if 'retweeted' in types else 'quote' if 'quoted' in types else 'reply' if 'replied_to' in types else 'original'),
        is_reply='replied_to' in types, is_quote='quoted' in types, is_repost='retweeted' in types,
        references=refs)


def fetch_latest(handle='elonmusk', limit=5):
    handle = username(handle)
    now = time.time()
    with db.connect() as con:
        record = _record(con, handle)
    # Return cached results even with missing/disabled credentials; never fallback to demo.
    if record.get('last_fetch') and now-record['last_fetch']<CACHE_SECONDS:
        return {**status(handle), 'code':'cached', 'message':MESSAGES['cached'], 'network_requests':0}
    token = os.environ.get('X_BEARER_TOKEN','').strip()
    try:
        if not token:
            raise XError('missing_credentials', 400)
        if os.environ.get('X_LIVE_ENABLED','false').lower() != 'true':
            raise XError('disabled', 400)
        if not 5<=limit<=10:
            raise XError('request_rejected', 422)
        user_cached = record.get('user_id') and now-record.get('resolved_at',0)<USER_CACHE_SECONDS
        _claim(handle, now, 1 if user_cached else 2)
        with client() as session:
            if not user_cached:
                payload = _get(session, '/users/by/username/'+handle, token)
                data = payload.get('data', {})
                if not isinstance(data,dict) or not isinstance(data.get('id'),str) or not data['id'].isdigit():
                    raise XError('invalid_response', 502)
                # Persist user lookup independently: a later timeline failure must not repeat its cost.
                with db.connect() as con:
                    record = _record(con, handle)
                    record.update(user_id=data['id'], resolved_at=now)
                    _store(con, handle, record)
            payload = _get(session, '/users/'+record['user_id']+'/tweets', token,
                params={'max_results':limit, 'tweet.fields':'created_at,public_metrics,referenced_tweets,author_id'})
        rows = payload.get('data')
        meta = payload.get('meta', {})
        if not isinstance(meta,dict):
            raise XError('invalid_response', 502)
        if rows is None and meta.get('result_count')==0:
            rows = []
        if not isinstance(rows,list) or len(rows)>limit:
            raise XError('invalid_response', 502)
        try:
            posts = [normalize_post(p,handle) for p in rows]
        except (ValueError, KeyError, TypeError, AttributeError):
            raise XError('invalid_response', 502) from None
        with db.connect() as con:
            for post in posts:
                con.execute('INSERT OR REPLACE INTO x_posts VALUES(?,?,?,?)',
                    (post['id'],handle,post['created_at'],json.dumps(post)))
            record = _record(con, handle)
            record.update(last_fetch=now,last_count=len(posts),code='success' if posts else 'empty')
            _store(con, handle, record)
        result = status(handle)
        result.update(code=record['code'],message=MESSAGES[record['code']],network_requests=1 if user_cached else 2)
        return result
    except XError as exc:
        with db.connect() as con:
            record = _record(con, handle)
            record['code'] = exc.code
            _store(con, handle, record)
        raise
