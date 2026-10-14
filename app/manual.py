"""User-entered X posts: validate and persist locally; never fetch a URL."""
from datetime import datetime, timezone
import json
import re
import sqlite3
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from . import db

router = APIRouter(prefix='/api/manual', tags=['manual imports'])
HOSTS = {'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com', 'mobile.twitter.com'}


class ManualPost(BaseModel):
    url: str = Field(min_length=10, max_length=2000)
    handle: str = Field(min_length=1, max_length=16)
    text: str = Field(min_length=1, max_length=25000)
    created_at: datetime
    likes: int | None = Field(default=None, ge=0, le=100000000000, strict=True)
    reposts: int | None = Field(default=None, ge=0, le=100000000000, strict=True)
    replies: int | None = Field(default=None, ge=0, le=100000000000, strict=True)

    @field_validator('handle')
    @classmethod
    def author(cls, value):
        value = value.strip().removeprefix('@').lower()
        if not re.fullmatch(r'[a-z0-9_]{1,15}', value):
            raise ValueError('Enter a valid X handle, with or without @')
        return value

    @field_validator('text')
    @classmethod
    def full_text(cls, value):
        if not value.strip():
            raise ValueError('Full post text cannot be blank')
        return value.strip()

    @field_validator('created_at')
    @classmethod
    def publication(cls, value):
        if value.tzinfo is None:
            raise ValueError('Publication time must include a timezone')
        if value > datetime.now(timezone.utc):
            raise ValueError('Publication time cannot be in the future')
        return value.astimezone(timezone.utc)

    @model_validator(mode='after')
    def source_url(self):
        try:
            parsed = urlsplit(self.url.strip())
        except ValueError:
            raise ValueError('Enter a valid HTTPS X post URL') from None
        match = re.fullmatch(r'/([A-Za-z0-9_]{1,15})/status/([0-9]{1,25})/?', parsed.path)
        if parsed.scheme != 'https' or parsed.netloc.lower() not in HOSTS or not match:
            raise ValueError('Use https://x.com/author/status/numeric-post-id (twitter.com links also accepted)')
        if match[1].lower() != self.handle:
            raise ValueError('Author handle must match the handle in the post URL')
        if int(match[2]) == 0:
            raise ValueError('Post ID must be a positive integer')
        self.url = f'https://x.com/{self.handle}/status/{int(match[2])}'
        return self


@router.post('/posts', status_code=201)
def save_post(value: ManualPost):
    x_id = value.url.rsplit('/', 1)[1]
    post = {**value.model_dump(mode='json'), 'id':'manual:'+x_id, 'x_id':x_id,
            'provenance':'manual_x', 'post_type':'manually entered', 'created_at':value.created_at.isoformat(),
            'imported_at':datetime.now(timezone.utc).isoformat()}
    try:
        with db.connect() as con:
            con.execute('INSERT INTO manual_posts VALUES(?,?,?,?)',
                (post['id'],post['handle'],post['created_at'],json.dumps(post)))
            con.execute('INSERT OR IGNORE INTO accounts(handle) VALUES(?)', (post['handle'],))
    except sqlite3.IntegrityError:
        raise HTTPException(409, 'This X post has already been manually imported. Its existing text and metrics were kept.') from None
    return {'post':post, 'message':'Saved locally. Choose Manual Imports and Analyze signals; no X request was made.'}


@router.get('/posts')
def recent_posts():
    with db.connect() as con:
        posts = [json.loads(r['payload']) for r in con.execute(
            'SELECT payload FROM manual_posts ORDER BY rowid DESC LIMIT 20')]
        total = con.execute('SELECT count(*) FROM manual_posts').fetchone()[0]
    return {'posts':posts, 'total':total}


def selected_posts(con):
    return [json.loads(r['payload']) for r in con.execute(
        'SELECT p.payload FROM manual_posts p JOIN accounts a ON p.handle=a.handle WHERE a.enabled=1')]
