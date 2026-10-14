from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from . import db, demo
from .trends import DEFAULT_BRIEF, detect
from .content import generate

STATIC = Path(__file__).parent / 'static'


@asynccontextmanager
async def lifespan(app):
    db.init()
    with db.connect() as con:
        if not con.execute("SELECT 1 FROM settings WHERE key='initialized'").fetchone():
            con.executemany('INSERT OR IGNORE INTO accounts(handle) VALUES(?)', [(h,) for h in demo.HANDLES])
            for p in demo.posts():
                con.execute('INSERT OR IGNORE INTO posts VALUES(:id,:handle,:text,:created_at,:likes,:reposts,:replies,:provenance)',p)
            con.execute("INSERT INTO settings VALUES('initialized','1')")
    yield


app = FastAPI(title='TelyClaw Growth Engine', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=STATIC), name='static')


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


@app.post('/api/analyze')
def analyze(value: Analyze):
    if value.hours not in (1,4,24,168) or value.mode not in ('demo','imported'):
        raise HTTPException(422,'Choose a supported window and dataset')
    clock = demo.CLOCK if value.mode=='demo' else datetime.now(timezone.utc)
    start, earlier = clock-timedelta(hours=value.hours), clock-timedelta(hours=value.hours*2)
    with db.connect() as con:
        rows = [dict(r) for r in con.execute('SELECT p.* FROM posts p JOIN accounts a ON p.handle=a.handle WHERE a.enabled=1 AND p.provenance=?',
                    ('synthetic' if value.mode=='demo' else 'imported',))]
        current = [p for p in rows if start <= datetime.fromisoformat(p['created_at']) <= clock]
        prior = [p for p in rows if earlier <= datetime.fromisoformat(p['created_at']) < start]
        brand = brief_value(con)
        result = dict(id=str(uuid4()), mode=value.mode, clock=clock.isoformat(), hours=value.hours,
            post_count=len(current), account_count=len({p['handle'] for p in current}),
            topics=detect(current,prior,clock,value.hours,brand), brief=brand,
            analyzed_at=datetime.now(timezone.utc).isoformat())
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
            mode=analysis['mode'], angles=angles, text=text, provider=provider, status='draft',
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
        result.update(status='approved',approved_at=datetime.now(timezone.utc).isoformat())
        save(con,'drafts',result)
    return result


@app.get('/api/drafts/{identifier}/export')
def export(identifier: str):
    with db.connect() as con:
        result = load(con,'drafts',identifier)
        if result['status'] != 'approved':
            raise HTTPException(409,'Human approval required before export')
    return PlainTextResponse(result['text'],headers={'Content-Disposition':'attachment; filename="approved-post.txt"'})
