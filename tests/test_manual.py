"""Manual importing is fully local; the global X client guard remains in place."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import db


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'manual.db'))
    with TestClient(app) as c:
        yield c


def post(identifier='100001',handle='growth_author',hours=.25,**changes):
    return {'url':f'https://x.com/{handle}/status/{identifier}', 'handle':'@'+handle,
        'text':'AI agents need human approval in growth workflows. Customer insight should guide content.',
        'created_at':(datetime.now(timezone.utc)-timedelta(hours=hours)).isoformat(),**changes}


def run(c,hours=4,mode='manual'):
    r=c.post('/api/analyze',json={'mode':mode,'hours':hours})
    assert r.status_code==200,r.text
    return r.json()


def test_save_optional_metrics_sources_and_restart(client):
    r=client.post('/api/manual/posts',json=post())
    assert r.status_code==201,r.text
    saved=r.json()['post']
    assert saved['provenance']=='manual_x' and saved['likes'] is None
    assert saved['handle']=='growth_author' and saved['created_at'].endswith('+00:00')
    assert client.get('/api/state').json()['manual_posts']==1
    assert run(client)['post_count']==1
    # A real second lifespan simulates restarting the app against the same DB.
    with TestClient(app) as restarted:
        assert restarted.get('/api/manual/posts').json()['posts'][0]==saved
        assert run(restarted)['post_count']==1
        assert restarted.get('/api/x/status').json()['requests_used']==0


def test_all_windows_multi_account_filtering(client):
    for i,hours in enumerate([.25,2,8,40,200]):
        assert client.post('/api/manual/posts',json=post(str(100+i),handle='author_'+str(i),hours=hours)).status_code==201
    assert [run(client,h)['post_count'] for h in (1,4,24,168)]==[1,2,3,4]
    assert run(client,168)['account_count']==4
    client.post('/api/accounts',json={'handle':'author_0','enabled':False})
    assert run(client,1)['post_count']==0
    assert client.get('/api/manual/posts').json()['total']==5


@pytest.mark.parametrize('url',[
    'https://twitter.com/Growth_Author/status/100001?s=20',
    'https://www.x.com/growth_author/status/100001/',
    'https://mobile.twitter.com/growth_author/status/100001#fragment'
])
def test_canonical_duplicate_prevention_preserves_original(client,url):
    assert client.post('/api/manual/posts',json=post(likes=0)).status_code==201
    duplicate=client.post('/api/manual/posts',json=post(url=url,text='Changed source',likes=999))
    assert duplicate.status_code==409
    saved=client.get('/api/manual/posts').json()['posts'][0]
    assert saved['likes']==0 and saved['text']!='Changed source'
    assert saved['url']=='https://x.com/growth_author/status/100001'
    assert client.get('/api/manual/posts').json()['total']==1


@pytest.mark.parametrize('changes',[
    {'url':'https://x.com.evil.example/growth_author/status/100001'},
    {'url':'https://x.com@evil.example/growth_author/status/100001'},
    {'url':'https://x.com:443/growth_author/status/100001'},
    {'url':'http://x.com/growth_author/status/100001'},
    {'url':'javascript:alert(1)'},
    {'url':'https://x.com/growth_author/status/not-a-number'},
    {'url':'https://x.com/other_author/status/100001'},
    {'url':'https://x.com/growth_author'},
    {'handle':'invalid handle'}, {'handle':'@'},{'text':'  '}, {'text':'x'*25001},
    {'created_at':'2026-01-01T12:00:00'}, {'created_at':'not-a-date'},
    {'created_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()},
    {'likes':-1},{'likes':1.5},{'likes':True},{'likes':'12'},{'reposts':-3},{'replies':100000000001},
])
def test_invalid_posts_are_atomic(client,changes):
    r=client.post('/api/manual/posts',json=post(**changes))
    assert r.status_code==422,r.text
    assert client.get('/api/manual/posts').json()['total']==0
    assert not any(a['handle']=='growth_author' for a in client.get('/api/state').json()['accounts'])


def test_mode_isolation_scoring_and_content_workflow(client):
    client.post('/api/manual/posts',json=post())
    assert run(client,4,'demo')['post_count']==20
    assert run(client,4,'imported')['post_count']==0
    assert run(client,4,'live')['post_count']==0
    analysis=run(client)
    assert 'Too few' in analysis['sample_warning']
    topic=analysis['topics'][0]
    assert topic['factors']['engagement'] is None and topic['weights']['engagement']==0
    assert sum(topic['weights'].values())==pytest.approx(1)
    d=client.post('/api/drafts',json={'analysis_id':analysis['id'],'topic_id':topic['id']}).json()
    assert d['mode']=='manual' and len(d['angles'])==3
    assert d['sources'][0]['url']=='https://x.com/growth_author/status/100001'
    assert 'user-supplied' in d['source_warning']
    path='/api/drafts/'+d['id']
    assert client.get(path+'/export').status_code==409
    assert client.put(path,json={'text':'Customer questions should guide AI growth. What should teams test first?'}).status_code==200
    assert client.post(path+'/approve').status_code==200
    assert client.get(path+'/export').status_code==200
    assert client.put(path,json={'text':'A changed draft needs review again.'}).json()['status']=='draft'
    assert client.get(path+'/export').status_code==409
    assert client.get('/api/x/status').json()['requests_used']==0


def test_warning_uses_unique_texts_and_account_breadth(client):
    for i in range(5):
        client.post('/api/manual/posts',json=post(str(300+i),handle='account_'+str(i)))
    assert '1 distinct texts' in run(client)['sample_warning']
    for i in range(5):
        client.post('/api/manual/posts',json=post(str(400+i),handle='new_author',text=[
            'AI agents need approval and accountable owners.',
            'Customer conversations reveal questions for marketing teams.',
            'Content attribution measures product clicks from buyers.',
            'Social listening can reveal customer insight before search volume.',
            'Growth experiments should compare qualified replies not raw impressions.'
        ][i]))
    result=run(client)
    assert result['sample_warning'] is None
    assert 'hand-selected' in result['source_warning']
    assert len(result['topics'])>=2


def test_empty_manual_mode_warns_and_does_not_fallback(client):
    value=run(client)
    assert value['topics']==[] and value['post_count']==0
    assert '0 distinct texts' in value['sample_warning']


def test_known_zero_metrics_retain_engagement_factor(client):
    client.post('/api/manual/posts',json=post(likes=0,reposts=0,replies=0))
    topic=run(client)['topics'][0]
    assert topic['factors']['engagement']==0 and topic['weights']['engagement']==pytest.approx(.20)


def test_concurrent_duplicate_saves(client):
    value=post()
    with ThreadPoolExecutor(max_workers=2) as executor:
        codes=list(executor.map(lambda _:client.post('/api/manual/posts',json=value).status_code,range(2)))
    assert sorted(codes)==[201,409]
    assert client.get('/api/manual/posts').json()['total']==1


def test_manual_database_upgrade_preserves_existing_data(client):
    client.post('/api/manual/posts',json=post())
    before=client.get('/api/state').json()
    db.init()
    after=client.get('/api/state').json()
    assert after['accounts']==before['accounts'] and after['manual_posts']==1
    assert after['imported_posts']==before['imported_posts']
