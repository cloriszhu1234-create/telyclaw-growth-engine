"""Manual publication records and cumulative metric snapshots; never posts to X."""
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
from urllib.parse import quote, urlsplit
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from . import db

router=APIRouter(prefix='/api',tags=['publishing and performance'])
METRICS=('impressions','likes','reposts','replies','bookmarks','link_clicks','profile_visits','attributed_followers')
ENGAGEMENT=('likes','reposts','replies','bookmarks')


def get_draft(con,identifier):
    row=con.execute('SELECT payload FROM drafts WHERE id=?',(identifier,)).fetchone()
    if not row:raise HTTPException(404,'Draft not found')
    return json.loads(row['payload'])


def canonical_url(value):
    try:parsed=urlsplit(value.strip())
    except ValueError:raise ValueError('Use an HTTPS X post URL') from None
    match=re.fullmatch(r'/([A-Za-z0-9_]{1,15})/status/([0-9]{1,25})/?',parsed.path)
    if parsed.scheme!='https' or parsed.netloc.lower() not in ('x.com','www.x.com','twitter.com','www.twitter.com','mobile.twitter.com') or not match or int(match[2])==0:
        raise ValueError('Use https://x.com/author/status/numeric-post-id')
    return f'https://x.com/{match[1].lower()}/status/{int(match[2])}',str(int(match[2]))


def valid_time(value):
    if value.tzinfo is None:raise ValueError('Timestamp must include timezone')
    if value>datetime.now(timezone.utc):raise ValueError('Timestamp cannot be in the future')
    return value.astimezone(timezone.utc)


class Publication(BaseModel):
    url:str=Field(min_length=10,max_length=2000)
    published_at:datetime

    @field_validator('url')
    @classmethod
    def check_url(cls,value):return canonical_url(value)[0]

    @field_validator('published_at')
    @classmethod
    def check_time(cls,value):return valid_time(value)


@router.get('/drafts/{identifier}/composer')
def composer(identifier:str):
    with db.connect() as con:
        draft=get_draft(con,identifier)
    if draft['status']!='approved':raise HTTPException(409,'Save and approve the current draft before opening X')
    return RedirectResponse('https://twitter.com/intent/tweet?text='+quote(draft['text'],safe=''),status_code=303)


@router.post('/drafts/{identifier}/publish',status_code=201)
def mark_published(identifier:str,value:Publication):
    with db.connect() as con:
        con.execute('BEGIN IMMEDIATE')
        draft=get_draft(con,identifier)
        if draft['status']!='approved':raise HTTPException(409,'Only an approved, unpublished draft can be marked published')
        publication=dict(id=str(uuid4()),draft_id=identifier,topic_title=draft['topic_title'],
            topic_key=draft.get('topic_key') or hashlib.sha256(draft['topic_title'].lower().encode()).hexdigest()[:20],
            text=draft['text'],mode=draft['mode'],url=value.url,x_id=canonical_url(value.url)[1],
            published_at=value.published_at.isoformat(),recorded_at=datetime.now(timezone.utc).isoformat(),
            provenance='User-confirmed manual publication; not verified with X')
        try:
            con.execute('INSERT INTO publications VALUES(?,?,?,?)',(publication['id'],identifier,publication['x_id'],json.dumps(publication)))
        except sqlite3.IntegrityError:
            raise HTTPException(409,'That X post or draft already has a publication record') from None
        draft.update(status='published',publication_id=publication['id'],published_url=value.url,published_at=publication['published_at'])
        con.execute('UPDATE drafts SET payload=? WHERE id=?',(json.dumps(draft),identifier))
    return publication


@router.post('/drafts/{identifier}/revision',status_code=201)
def revision(identifier:str):
    with db.connect() as con:
        draft=get_draft(con,identifier)
        for key in ('publication_id','published_url','published_at'):
            draft.pop(key,None)
        draft.update(id=str(uuid4()),status='draft',approved_at=None,created_at=datetime.now(timezone.utc).isoformat(),updated_at=datetime.now(timezone.utc).isoformat())
        con.execute('INSERT INTO drafts VALUES(?,?)',(draft['id'],json.dumps(draft)))
    return draft


class Measurement(BaseModel):
    measured_at:datetime
    impressions:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    likes:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    reposts:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    replies:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    bookmarks:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    link_clicks:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    profile_visits:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    attributed_followers:int|None=Field(default=None,ge=0,le=100000000000,strict=True)
    attribution_evidence:str|None=Field(default=None,max_length=2000)

    @field_validator('measured_at')
    @classmethod
    def check_time(cls,value):return valid_time(value)

    @model_validator(mode='after')
    def attribution(self):
        if self.attributed_followers is not None and (not self.attribution_evidence or len(self.attribution_evidence.strip())<10):
            raise ValueError('Post-attributed followers require a description of reliable attribution evidence; account-level growth is not post attribution')
        return self


@router.post('/publications/{identifier}/measurements',status_code=201)
def measure(identifier:str,value:Measurement):
    with db.connect() as con:
        con.execute('BEGIN IMMEDIATE')
        row=con.execute('SELECT payload FROM publications WHERE id=?',(identifier,)).fetchone()
        if not row:raise HTTPException(404,'Publication not found')
        pub=json.loads(row['payload'])
        if value.measured_at<datetime.fromisoformat(pub['published_at']):
            raise HTTPException(422,'Measurement must be at or after publication')
        latest=con.execute('SELECT measured_at FROM measurements WHERE publication_id=? ORDER BY measured_at DESC LIMIT 1',(identifier,)).fetchone()
        if latest and value.measured_at<datetime.fromisoformat(latest['measured_at']):
            raise HTTPException(409,'Enter a measurement timestamp at or after the latest snapshot')
        result={**value.model_dump(mode='json'),'id':str(uuid4()),'publication_id':identifier,'measured_at':value.measured_at.isoformat(),'provenance':'Manual cumulative metric snapshot; unverified'}
        con.execute('INSERT INTO measurements VALUES(?,?,?,?)',(result['id'],identifier,result['measured_at'],json.dumps(result)))
    return result


def calculations(metrics):
    metrics=metrics or {}
    observed=[metrics[k] for k in ENGAGEMENT if metrics.get(k) is not None]
    total=sum(observed) if observed else None
    impressions=metrics.get('impressions')
    return dict(total_engagement=total,engagement_complete=all(metrics.get(k) is not None for k in ENGAGEMENT),
        engagement_rate=round(total/impressions*100,3) if impressions and total is not None else None,
        missing_engagement=[k for k in ENGAGEMENT if metrics.get(k) is None])


def aggregate(posts):
    sums={k:sum(p['metrics'][k] for p in posts if p['metrics'].get(k) is not None)
        if any(p['metrics'].get(k) is not None for p in posts) else None for k in METRICS}
    # Aggregate rate uses only posts with positive impressions and some measured engagement.
    paired=[p for p in posts if p['metrics'].get('impressions') and p['calculated']['total_engagement'] is not None]
    denominator=sum(p['metrics']['impressions'] for p in paired)
    return dict(posts=len(posts),measured_posts=sum(any(p['metrics'].get(k) is not None for k in METRICS) for p in posts),totals=sums,
        **{k:v for k,v in calculations(sums).items() if k not in ('engagement_rate','engagement_complete')},
        engagement_complete=bool(posts) and all(p['calculated']['engagement_complete'] for p in posts),
        engagement_rate=round(sum(p['calculated']['total_engagement'] for p in paired)/denominator*100,3) if denominator else None,
        rate_posts=len(paired),metric_coverage={k:sum(p['metrics'].get(k) is not None for p in posts) for k in METRICS})


@router.get('/performance')
def performance():
    with db.connect() as con:
        posts=[]
        for row in con.execute('SELECT payload FROM publications ORDER BY rowid DESC'):
            pub=json.loads(row['payload'])
            snapshots=[json.loads(r['payload']) for r in con.execute('SELECT payload FROM measurements WHERE publication_id=? ORDER BY measured_at DESC,rowid DESC',(pub['id'],))]
            metrics=snapshots[0] if snapshots else {}
            posts.append({**pub,'metrics':metrics,'calculated':calculations(metrics),'snapshots':snapshots})
    groups={}
    for post in posts:groups.setdefault(post['topic_key'],[]).append(post)
    return dict(posts=posts,aggregate=aggregate(posts),topics=[dict(topic_key=key,title=rows[0]['topic_title'],**aggregate(rows)) for key,rows in groups.items()],
        formula='Measured engagement = available likes + reposts + replies + bookmarks. Partial counts are labeled; unknown is not zero. Rate = measured engagement / impressions × 100. Clicks, profile visits and attributed followers are separate outcomes, not added again.',
        warning='Manual metrics are unverified and are not automatically qualified engagement. Snapshots are cumulative; only the latest per post is aggregated. Account-level follower growth must not be entered as post-attributed followers.')
