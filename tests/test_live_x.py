"""All outbound X traffic is mocked; placeholder credentials have no real value."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
import sqlite3
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from app import db, x_api
from app.main import app
from app.trends import DEFAULT_BRIEF, detect

# Fixed clock makes cooldown/day-boundary assertions deterministic.
NOW = datetime(2026,10,14,10,tzinfo=timezone.utc).timestamp()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path/'live.db'))
    monkeypatch.setattr(x_api.time,'time',lambda:NOW)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def transport(monkeypatch):
    calls=[]
    def install(handler=None):
        monkeypatch.setenv('X_BEARER_TOKEN','non-secret-test-placeholder')
        monkeypatch.setenv('X_LIVE_ENABLED','true')
        def route(request):
            calls.append(request)
            assert request.url.host=='api.x.com'
            assert request.method=='GET'
            return handler(request) if handler else standard(request)
        monkeypatch.setattr(x_api,'client',lambda:httpx.Client(transport=httpx.MockTransport(route)))
        return calls
    return install


def tweet(i='101',type=None,metrics=True):
    result={'id':i,'text':'AI agents need human approval in growth workflows. Customer trust matters.',
        'created_at':(datetime.now(timezone.utc)-timedelta(minutes=15)).isoformat(),'author_id':'44196397'}
    if type:
        result['referenced_tweets']=[{'id':'99','type':type}]
    if metrics:
        result['public_metrics']={'like_count':100,'retweet_count':5,'reply_count':3,'quote_count':2}
    return result


def standard(request):
    if '/by/username/' in request.url.path:
        return httpx.Response(200,json={'data':{'id':'44196397','username':'elonmusk'}})
    return httpx.Response(200,json={'data':[tweet(),tweet('102','replied_to'),tweet('103','quoted'),tweet('104','retweeted',False)],'meta':{'result_count':4}})


def fetch(c,**kwargs):
    return c.post('/api/x/fetch',json={'username':'elonmusk',**kwargs})


def expire(monkeypatch,offset=901):
    monkeypatch.setattr(x_api.time,'time',lambda:NOW+offset)


def test_missing_credentials_and_disabled_gate(client, transport, monkeypatch):
    assert client.get('/api/x/status').json()['code']=='missing_credentials'
    assert fetch(client).json()['detail']['code']=='missing_credentials'
    calls=transport()
    monkeypatch.setenv('X_LIVE_ENABLED','false')
    assert fetch(client).json()['detail']['code']=='disabled'
    assert client.get('/api/x/status').json()['requests_used']==0
    assert not calls


def test_fetch_official_endpoints_and_normalization(client, transport):
    calls=transport()
    r=fetch(client)
    assert r.status_code==200,r.text
    assert r.json()['last_retrieved']==4 and r.json()['network_requests']==2
    assert calls[0].url.path=='/2/users/by/username/elonmusk'
    assert calls[1].url.path=='/2/users/44196397/tweets'
    assert calls[1].url.params['max_results']=='5'
    assert 'referenced_tweets' in calls[1].url.params['tweet.fields']
    assert all(request.headers['Authorization'].startswith('Bearer ') for request in calls)
    rows=x_api.cached_posts('elonmusk')
    assert len(rows)==4 and {p['post_type'] for p in rows}=={'original','quote','reply','repost'}
    assert all(p['url']==f"https://x.com/elonmusk/status/{p['x_id']}" for p in rows)
    assert all(p['created_at'].endswith('+00:00') for p in rows)
    missing=next(p for p in rows if p['post_type']=='repost')
    assert missing['likes'] is None and missing['impressions'] is None
    assert 'non-secret-test-placeholder' not in r.text
    with db.connect() as con:
        for table in ('x_accounts','x_posts','x_control','x_requests','settings'):
            assert 'non-secret-test-placeholder' not in str([tuple(x) for x in con.execute('SELECT * FROM '+table)])


@pytest.mark.parametrize('status,body,code',[
    (401,{'detail':'private upstream message'},'authentication_error'),
    (403,{'detail':'private upstream message'},'access_denied'),
    (402,{'title':'CreditsDepleted'},'insufficient_credits'),
    (403,{'title':'CreditsDepleted'},'insufficient_credits'),
    (429,{'title':'Too Many Requests'},'rate_limited'),
    (404,{},'account_not_found'),
    (500,{},'service_error'),
])
def test_safe_errors_no_retries_or_demo_substitution(client, transport, status, body, code):
    calls=transport(lambda request:httpx.Response(status,json=body,headers={'x-rate-limit-reset':str(int(NOW+2000))}))
    r=fetch(client)
    assert r.status_code>=400 and r.json()['detail']['code']==code
    assert len(calls)==1
    assert 'private upstream' not in r.text
    assert not x_api.cached_posts('elonmusk')
    assert client.get('/api/x/status').json()['requests_used']==1


def test_network_error_sanitized(client, transport):
    def fail(request):
        raise httpx.ConnectError('sensitive network diagnostics',request=request)
    calls=transport(fail)
    r=fetch(client)
    assert r.json()['detail']['code']=='network_error'
    assert 'sensitive' not in r.text and len(calls)==1


def test_post_and_user_cache_deduplication_and_metrics_update(client, transport, monkeypatch):
    calls=transport()
    assert fetch(client).status_code==200
    assert fetch(client).json()['code']=='cached' and len(calls)==2
    expire(monkeypatch)
    assert fetch(client).status_code==200
    assert len(calls)==3  # resolved user ID was reused
    assert len(x_api.cached_posts('elonmusk'))==4
    assert client.get('/api/x/status').json()['requests_used']==3
    # Cached data remains analyzable even after the token is removed.
    monkeypatch.setenv('X_BEARER_TOKEN','')
    assert fetch(client).json()['network_requests']==0
    assert client.get('/api/x/status').json()['credentials_configured'] is False


def test_cache_retained_on_later_error(client, transport, monkeypatch):
    transport();fetch(client)
    expire(monkeypatch)
    calls=transport(lambda request:httpx.Response(402,json={'title':'CreditsDepleted'}))
    initial=len(calls)
    assert fetch(client).json()['detail']['code']=='insufficient_credits'
    state=client.get('/api/x/status').json()
    assert state['cached_posts']==4 and state['last_fetch'] and not state['cache_fresh']
    assert len(calls)==initial+1
    run=client.post('/api/analyze',json={'mode':'live','hours':24}).json()
    assert run['post_count']>0 and all(p['provenance']=='live_x' for t in run['topics'] for p in t['evidence'])


def test_global_cooldown_and_daily_cap_persist(client, transport, monkeypatch):
    calls=transport()
    fetch(client)
    r=fetch(client,username='another_user')
    assert r.json()['detail']['code']=='cooldown' and len(calls)==2
    expire(monkeypatch)
    with db.connect() as con:
        con.executemany('INSERT INTO x_requests(attempted_at) VALUES(?)',[(NOW,)]*8)
    r=fetch(client)
    assert r.json()['detail']['code']=='daily_cap' and len(calls)==2
    db.init()  # restart/migration never resets budget
    assert client.get('/api/x/status').json()['requests_used']==10
    expire(monkeypatch,86401)
    assert fetch(client).status_code==200
    assert client.get('/api/x/status').json()['requests_used']==1


def test_rate_limit_reset_honored_across_handles(client, transport, monkeypatch):
    calls=transport(lambda request:httpx.Response(429,json={},headers={'x-rate-limit-reset':str(int(NOW+7200))}))
    assert fetch(client).json()['detail']['retry_at']==x_api.stamp(NOW+7200)
    expire(monkeypatch,3600)
    assert fetch(client,username='another_user').json()['detail']['code']=='rate_limited'
    assert len(calls)==1


def test_success_remaining_zero_prevents_next_network_request(client, transport, monkeypatch):
    def handler(request):
        r=standard(request)
        if request.url.path.endswith('/tweets'):
            r.headers.update({'x-rate-limit-remaining':'0','x-rate-limit-reset':str(int(NOW+7200))})
        return r
    calls=transport(handler)
    assert fetch(client).status_code==200
    expire(monkeypatch)
    assert fetch(client).json()['detail']['code']=='rate_limited'
    assert len(calls)==2


@pytest.mark.parametrize('payload',[
    {'data':[{'id':'bad'}]}, {'data':'bad'}, {'errors':[{'detail':'private'}]}, {'data':[tweet(metrics=False)]*6},
])
def test_malformed_timeline_preserves_integrity(client, transport, payload):
    transport(lambda req:standard(req) if '/by/username/' in req.url.path else httpx.Response(200,json=payload))
    r=fetch(client)
    assert r.json()['detail']['code']=='invalid_response'
    assert not x_api.cached_posts('elonmusk')


def test_empty_live_response_and_mode_isolation(client, transport):
    calls=transport(lambda req:standard(req) if '/by/username/' in req.url.path else httpx.Response(200,json={'meta':{'result_count':0}}))
    assert fetch(client).json()['code']=='empty'
    assert client.post('/api/analyze',json={'mode':'live','hours':4}).json()['topics']==[]
    demo=client.post('/api/analyze',json={'mode':'demo','hours':4}).json()
    assert len(demo['topics'])>=3 and demo['post_count']==20
    assert client.post('/api/analyze',json={'mode':'imported','hours':4}).json()['topics']==[]
    assert len(calls)==2


def test_live_analysis_content_approval_export_and_missing_metrics(client, transport):
    calls=transport();fetch(client)
    run=client.post('/api/analyze',json={'mode':'live','hours':168}).json()
    assert 'not a platform-wide trend' in run['source_warning']
    assert run['account_count']==1
    # Make all records missing metrics to verify excluded weights rather than invented zeros.
    rows=x_api.cached_posts('elonmusk')
    for row in rows:
        row['likes']=None
    topics=detect(rows,[],datetime.fromtimestamp(NOW,timezone.utc),24,DEFAULT_BRIEF)
    for topic in topics:
        assert topic['factors']['engagement'] is None and topic['weights']['engagement']==0
        assert sum(topic['weights'].values())==pytest.approx(1)
        assert 0<=topic['score']<=100
        assert 'Single-account signal' in topic['reason']
    d=client.post('/api/drafts',json={'analysis_id':run['id'],'topic_id':run['topics'][0]['id']}).json()
    assert len(d['angles'])==3 and d['mode']=='live' and d['sources'][0]['url'].startswith('https://x.com/')
    assert d['text'] not in [p['text'] for p in rows]
    assert client.get('/api/drafts/'+d['id']+'/export').status_code==409
    assert client.post('/api/drafts/'+d['id']+'/approve').status_code==200
    assert client.get('/api/drafts/'+d['id']+'/export').text==d['text']
    assert len(calls)==2  # analysis and content never initiate X traffic


def test_status_and_page_load_do_not_fetch(client, transport):
    calls=transport()
    for path in ['/','/api/state','/api/x/status?username=elonmusk']:
        assert client.get(path).status_code==200
    assert client.post('/api/analyze',json={'mode':'live','hours':4}).json()['post_count']==0
    assert not calls


def test_input_and_cross_origin_protection(client, transport):
    calls=transport()
    for data in [{'username':'evil/host'},{'username':'elonmusk','limit':100},{'limit':4}]:
        assert client.post('/api/x/fetch',json=data).status_code==422
    assert client.post('/api/x/fetch',json={},headers={'Origin':'https://other.example'}).status_code==403
    assert client.post('/api/x/fetch',json={},headers={'Sec-Fetch-Site':'cross-site'}).status_code==403
    assert not calls


def test_concurrent_fetches_cannot_bypass_cooldown(client, transport):
    calls=transport()
    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(lambda _:fetch(client),range(2)))
    assert any(r.status_code==200 for r in results)
    assert len(calls)==2


def test_normalization_combined_flags_and_missing_metrics():
    value=tweet()
    value['referenced_tweets']=[{'type':'quoted','id':'98'},{'type':'replied_to','id':'99'}]
    value['public_metrics']={'like_count':0}
    result=x_api.normalize_post(value,'elonmusk')
    assert result['is_quote'] and result['is_reply'] and result['post_type']=='quote'
    assert result['likes']==0 and result['replies'] is None
    assert result['references'][0]['id']=='98'


def test_lookup_rate_exhaustion_stops_timeline_request(client, transport):
    def handler(request):
        return httpx.Response(200,json={'data':{'id':'44196397'}},headers={
            'x-rate-limit-remaining':'0','x-rate-limit-reset':str(int(NOW+3600))})
    calls=transport(handler)
    r=fetch(client)
    assert r.json()['detail']['code']=='rate_limited'
    assert len(calls)==1
    assert client.get('/api/x/status').json()['requests_used']==1


def test_lookup_cache_survives_failed_timeline(client, transport, monkeypatch):
    def handler(request):
        return standard(request) if '/by/username/' in request.url.path else httpx.Response(403,json={})
    calls=transport(handler)
    assert fetch(client).json()['detail']['code']=='access_denied'
    expire(monkeypatch)
    transport()
    assert fetch(client).status_code==200
    assert len(calls)==3  # the failed timeline's resolved user ID was persisted
    assert sum('/by/username/' in call.url.path for call in calls)==1


@pytest.mark.parametrize('header', ['7200','Wed, 14 Oct 2026 12:00:00 GMT'])
def test_retry_after_seconds_or_http_date(client, transport, header):
    transport(lambda request:httpx.Response(429,json={},headers={'Retry-After':header}))
    assert fetch(client).json()['detail']['retry_at']==x_api.stamp(NOW+7200)


def test_invalid_json_and_lookup_payload_are_sanitized(client, transport, monkeypatch):
    calls=transport(lambda request:httpx.Response(200,text='not JSON; private provider diagnostics'))
    assert fetch(client).json()['detail']['code']=='invalid_response'
    assert len(calls)==1
    expire(monkeypatch)
    transport(lambda request:httpx.Response(200,json={'data':{'id':'unsafe/path'}}))
    assert fetch(client).json()['detail']['code']=='invalid_response'
    assert len(calls)==2  # no timeline requests made


def test_known_zero_metrics_are_not_missing(client, transport):
    row=x_api.normalize_post({**tweet(),'public_metrics':{'like_count':0,'retweet_count':0,'reply_count':0}},'elonmusk')
    topics=detect([row],[],datetime.now(timezone.utc),4,DEFAULT_BRIEF)
    assert topics[0]['factors']['engagement']==0
    assert topics[0]['weights']['engagement']==pytest.approx(.15)


def test_dedup_replaces_updated_metrics(client, transport, monkeypatch):
    calls=transport();fetch(client)
    expire(monkeypatch)
    changed=tweet();changed['public_metrics']['like_count']=999
    transport(lambda request:httpx.Response(200,json={'data':[changed]}))
    assert fetch(client).status_code==200
    rows=x_api.cached_posts('elonmusk')
    assert len(rows)==4
    assert next(p for p in rows if p['x_id']=='101')['likes']==999


def test_new_account_needs_two_budget_slots(client, transport):
    calls=transport()
    with db.connect() as con:
        con.executemany('INSERT INTO x_requests(attempted_at) VALUES(?)',[(NOW,)]*9)
    assert fetch(client).json()['detail']['code']=='daily_cap'
    assert not calls


def test_user_cache_ttl_and_additional_username(client, transport, monkeypatch):
    calls=transport();fetch(client)
    expire(monkeypatch,8*86400)
    assert fetch(client,username='@Other_User').status_code==200
    assert calls[-2].url.path=='/2/users/by/username/other_user'
    assert all(row['handle']=='other_user' for row in x_api.cached_posts('other_user'))
    expire(monkeypatch,8*86400+901)
    assert fetch(client).status_code==200
    assert calls[-2].url.path=='/2/users/by/username/elonmusk'  # expired 7-day ID cache


def test_additive_upgrade_preserves_existing_database(tmp_path,monkeypatch):
    path=tmp_path/'existing.db'
    monkeypatch.setenv('DATABASE_PATH',str(path))
    with sqlite3.connect(path) as con:
        con.executescript('''CREATE TABLE accounts(handle TEXT PRIMARY KEY,enabled INTEGER NOT NULL DEFAULT 1);
          CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE TABLE drafts(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
          INSERT INTO accounts VALUES('existing_source',0);
          INSERT INTO settings VALUES('initialized','1');''')
        con.execute('INSERT INTO drafts VALUES(?,?)',('saved-draft',json.dumps({'id':'saved-draft','text':'Keep this draft','status':'approved'})))
    with TestClient(app) as upgraded:
        state=upgraded.get('/api/state').json()
        assert state['accounts']==[{'handle':'existing_source','enabled':0}]
        assert state['drafts'][0]['text']=='Keep this draft'
        assert state['drafts'][0]['status']=='approved'
        assert upgraded.get('/api/x/status').json()['requests_used']==0


def test_expired_rate_status_becomes_ready_without_fetch(client,transport,monkeypatch):
    calls=transport(lambda request:httpx.Response(429,json={},headers={'Retry-After':'7200'}))
    fetch(client)
    expire(monkeypatch,7201)
    value=client.get('/api/x/status').json()
    assert value['code']=='ready' and value['next_fetch_at'] is None
    assert len(calls)==1  # local inspection never retries X
