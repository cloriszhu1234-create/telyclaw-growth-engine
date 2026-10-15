from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from . import db, demo, x_api, manual, publishing
from dotenv import load_dotenv
from .trends import DEFAULT_BRIEF, detect
from .content import generate

STATIC = Path(__file__).parent / 'static'


@asynccontextmanager
async def lifespan(app):
    load_dotenv(Path(__file__).resolve().parents[1] / '.env', override=False)
    db.init()
    with db.connect() as con:
        if not con.execute("SELECT 1 FROM settings WHERE key='initialized'").fetchone():
            con.executemany('INSERT OR IGNORE INTO accounts(handle) VALUES(?)', [(h,) for h in demo.HANDLES])
            for p in demo.posts():
                con.execute('INSERT OR IGNORE INTO posts VALUES(:id,:handle,:text,:created_at,:likes,:reposts,:replies,:provenance)',p)
            con.execute("INSERT INTO settings VALUES('initialized','1')")
    yield


app = FastAPI(title='TelyClaw Growth Engine', lifespan=lifespan)
app.include_router(manual.router)
app.include_router(publishing.router)
app.mount('/static', StaticFiles(directory=STATIC), name='static')


@app.exception_handler(x_api.XError)
async def x_error(request: Request, exc: x_api.XError):
    return JSONResponse(status_code=exc.status, content={'detail': {
        'code':exc.code, 'message':str(exc), 'retry_at':x_api.stamp(exc.retry_at)}})


@app.get('/api/x/status')
def x_status(username: str = Query(default='elonmusk', pattern=r'^@?[A-Za-z0-9_]{1,15}$')):
    # Local cache/config inspection only. Never contacts X.
    return x_api.status(username)


class FetchX(BaseModel):
    username: str = Field(default='elonmusk', pattern=r'^@?[A-Za-z0-9_]{1,15}$')
    limit: int = Field(default=5, ge=5, le=10)


@app.post('/api/x/fetch')
def fetch_x(value: FetchX, request: Request):
    # Browser cross-site requests must never spend the local user's API budget.
    origin = request.headers.get('origin')
    if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and origin.rstrip('/') != str(request.base_url).rstrip('/')):
        raise HTTPException(403, 'Cross-origin live fetching is not allowed')
    return x_api.fetch_latest(value.username, value.limit)


@app.get('/')
def home():
    return FileResponse(STATIC/'index.html')


def load(con, table, identifier):
    row = con.execute(f'SELECT payload FROM {table} WHERE id=?',(identifier,)).fetchone()
    if not row:
        raise HTTPException(404,'Record not found')
    return json.loads(row['payload'])


def save(con, table, value):
    con.execute(f'INSERT OR REPLACE INTO {table} VALUES(?,?)',(value['id'],json.dumps(value)))


def brief_value(con):
    row = con.execute("SELECT value FROM settings WHERE key='brief'").fetchone()
    return json.loads(row['value']) if row else DEFAULT_BRIEF


@app.get('/api/state')
def state():
    with db.connect() as con:
        return dict(accounts=[dict(r) for r in con.execute('SELECT * FROM accounts ORDER BY handle')],
            drafts=[json.loads(r['payload']) for r in con.execute('SELECT payload FROM drafts ORDER BY rowid DESC')],
            brief=brief_value(con), demo_clock=demo.CLOCK.isoformat(),
            manual_posts=con.execute('SELECT count(*) FROM manual_posts').fetchone()[0],
            imported_posts=con.execute("SELECT count(*) FROM posts WHERE provenance='imported'").fetchone()[0])


class Account(BaseModel):
    handle: str = Field(min_length=1,max_length=15,pattern=r'^[A-Za-z0-9_]+$')
    enabled: bool = True


@app.post('/api/accounts')
def account(value: Account):
    with db.connect() as con:
        con.execute('INSERT OR REPLACE INTO accounts VALUES(?,?)',(value.handle.lower(),int(value.enabled)))
    return {'ok':True}


@app.delete('/api/accounts/{handle}')
def remove_account(handle: str):
    with db.connect() as con:
        con.execute('DELETE FROM accounts WHERE handle=?',(handle,))
    return {'ok':True}


class Brief(BaseModel):
    positioning: str = Field(min_length=5,max_length=2000)
    audience: str = Field(min_length=3,max_length=300)
    keywords: list[str] = Field(min_length=1,max_length=30)

    @field_validator('keywords')
    @classmethod
    def clean_keywords(cls,value):
        if any(not x.strip() or len(x)>60 for x in value):
            raise ValueError('Keywords must contain 1–60 characters')
        return list(dict.fromkeys(x.strip().lower() for x in value))


@app.put('/api/brief')
def brief(value: Brief):
    with db.connect() as con:
        con.execute("INSERT OR REPLACE INTO settings VALUES('brief',?)",(value.model_dump_json(),))
    return {'ok':True}


class Post(BaseModel):
    id: str = Field(min_length=1,max_length=100)
    handle: str = Field(min_length=1,max_length=15,pattern=r'^[A-Za-z0-9_]+$')
    text: str = Field(min_length=1,max_length=5000)
    created_at: datetime
    likes: int = Field(default=0,ge=0,le=100000000)
    reposts: int = Field(default=0,ge=0,le=100000000)
    replies: int = Field(default=0,ge=0,le=100000000)

    @field_validator('created_at')
    @classmethod
    def timestamp(cls,value):
        if value.tzinfo is None:
            raise ValueError('Timestamp must include timezone')
        if value > datetime.now(timezone.utc)+timedelta(minutes=5):
            raise ValueError('Future post timestamps are not accepted')
        return value.astimezone(timezone.utc)


class Import(BaseModel):
    posts: list[Post] = Field(min_length=1,max_length=1000)


@app.post('/api/import')
def import_posts(value: Import):
    with db.connect() as con:
        for item in value.posts:
            p = item.model_dump()
            p.update(id='import:'+p['id'], handle=p['handle'].lower(), created_at=p['created_at'].isoformat(), provenance='imported')
            con.execute('INSERT OR REPLACE INTO posts VALUES(:id,:handle,:text,:created_at,:likes,:reposts,:replies,:provenance)',p)
            con.execute('INSERT OR IGNORE INTO accounts(handle) VALUES(?)',(p['handle'],))
    return {'imported':len(value.posts)}


class Analyze(BaseModel):
    hours: int = 4
    mode: str = 'demo'
    username: str = Field(default='elonmusk', pattern=r'^@?[A-Za-z0-9_]{1,15}$')


@app.post('/api/analyze')
def analyze(value: Analyze):
    if value.hours not in (1,4,24,168) or value.mode not in ('demo','imported','live','manual'):
        raise HTTPException(422,'Choose a supported window and dataset')
    clock = demo.CLOCK if value.mode=='demo' else datetime.now(timezone.utc)
    start, earlier = clock-timedelta(hours=value.hours), clock-timedelta(hours=value.hours*2)
    with db.connect() as con:
        if value.mode == 'live':
            rows = x_api.cached_posts(x_api.username(value.username))
        elif value.mode == 'manual':
            rows = manual.selected_posts(con)
        else:
            rows = [dict(r) for r in con.execute('SELECT p.* FROM posts p JOIN accounts a ON p.handle=a.handle WHERE a.enabled=1 AND p.provenance=?',
                        ('synthetic' if value.mode=='demo' else 'imported',))]
        current = [p for p in rows if start <= datetime.fromisoformat(p['created_at']) <= clock]
        prior = [p for p in rows if earlier <= datetime.fromisoformat(p['created_at']) < start]
        brand = brief_value(con)
        sample_warning = None
        manual_warning = None
        if value.mode == 'manual':
            unique_texts = len({re.sub(r'\W+', ' ', p['text'].lower()).strip() for p in current})
            authors = len({p['handle'] for p in current})
            if unique_texts < 5 or authors < 2:
                sample_warning = (f'Too few imported posts for reliable trend analysis: {unique_texts} distinct texts from {authors} accounts in this window. '
                    'Add at least 5 distinct posts from 2 or more accounts as a starting point; this is a demo heuristic, not a statistical guarantee.')
            manual_warning = 'Manually entered X posts: source text, dates, authors and metrics are user-supplied and unverified. A hand-selected sample does not establish platform-wide trends.'
        result = dict(id=str(uuid4()), mode=value.mode, clock=clock.isoformat(), hours=value.hours,
            post_count=len(current), account_count=len({p['handle'] for p in current}),
            topics=detect(current,prior,clock,value.hours,brand), brief=brand,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
            source_warning=('This is a cached sample from @'+x_api.username(value.username)+
                ', not a platform-wide trend. One account cannot establish cross-account momentum. '
                'Replies, quotes and reposts are labeled; fetched time windows may be incomplete.' if value.mode=='live' else manual_warning),
            sample_warning=sample_warning,
            live_status=x_api.status(value.username) if value.mode=='live' else None)
        save(con,'analyses',result)
    return result


class Generate(BaseModel):
    analysis_id: str
    topic_id: str


@app.post('/api/drafts')
def draft(value: Generate):
    with db.connect() as con:
        analysis = load(con,'analyses',value.analysis_id)
        topic = next((t for t in analysis['topics'] if t['id']==value.topic_id),None)
        if not topic:
            raise HTTPException(404,'Topic not found')
        try:
            angles,text,provider = generate(topic,analysis['brief'])
        except Exception:
            # Never leak credentials or silently substitute a provider after failure.
            raise HTTPException(502,'AI provider failed. Check server configuration or remove the key to use labeled local templates.')
        now = datetime.now(timezone.utc).isoformat()
        result = dict(id=str(uuid4()), analysis_id=analysis['id'], topic_id=topic['id'], topic_title=topic['title'],
            mode=analysis['mode'], topic_key=topic.get('topic_key'), sources=[{'handle':p['handle'],'url':p.get('url'),'post_type':p.get('post_type'),'provenance':p['provenance']} for p in topic['evidence']],
            source_warning=analysis.get('source_warning'), angles=angles, text=text, provider=provider, status='draft',
            created_at=now, updated_at=now, approved_at=None)
        save(con,'drafts',result)
    return result


class Edit(BaseModel):
    text: str = Field(min_length=1,max_length=280)

    @field_validator('text')
    @classmethod
    def safe_text(cls,value):
        if not value.strip():
            raise ValueError('Draft cannot be blank')
        if re.search(r'https?://|[^\x00-\x7f]',value):
            raise ValueError('This MVP validates plain ASCII posts without URLs; simplify the text before approval.')
        return value


@app.put('/api/drafts/{identifier}')
def edit_draft(identifier: str, value: Edit):
    with db.connect() as con:
        result = load(con,'drafts',identifier)
        if result['text'] != value.text and result['status']=='published':
            raise HTTPException(409,'Published text is preserved. Create a revision to edit a new draft.')
        if result['text'] != value.text:
            result.update(text=value.text,status='draft',approved_at=None,updated_at=datetime.now(timezone.utc).isoformat())
        save(con,'drafts',result)
    return result


@app.post('/api/drafts/{identifier}/approve')
def approve(identifier: str):
    with db.connect() as con:
        result = load(con,'drafts',identifier)
        try:
            Edit(text=result['text'])
        except ValueError:
            raise HTTPException(422,'Draft must be 1–280 ASCII characters without URLs')
        if result['status']=='published':
            return result
        result.update(status='approved',approved_at=datetime.now(timezone.utc).isoformat())
        save(con,'drafts',result)
    return result


@app.get('/api/drafts/{identifier}/export')
def export(identifier: str):
    with db.connect() as con:
        result = load(con,'drafts',identifier)
        if result['status'] not in ('approved','published'):
            raise HTTPException(409,'Human approval required before export')
    return PlainTextResponse(result['text'],headers={'Content-Disposition':'attachment; filename="approved-post.txt"'})
