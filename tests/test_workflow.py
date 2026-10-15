"""Behavioral acceptance and integrity checks, using isolated SQLite databases."""
from datetime import datetime, timedelta, timezone
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import db
from app.trends import DEFAULT_BRIEF, WEIGHTS, detect
from app.demo import CLOCK


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'))
    monkeypatch.setenv('OPENAI_API_KEY','')
    with TestClient(app) as client:
        yield client


def analysis(client, hours=4):
    r=client.post('/api/analyze',json={'hours':hours,'mode':'demo'})
    assert r.status_code==200,r.text
    return r.json()


def make_draft(client):
    run=analysis(client)
    response=client.post('/api/drafts',json={'analysis_id':run['id'],'topic_id':run['topics'][0]['id']})
    assert response.status_code==200,response.text
    return response.json()


def test_minimum_accounts_time_windows_and_topics(client):
    assert len(client.get('/api/state').json()['accounts'])>=5
    runs=[analysis(client,h) for h in (1,4,24,168)]
    assert all(len(run['topics'])>=3 for run in runs)
    assert runs[0]['post_count']<runs[1]['post_count']<runs[2]['post_count']<runs[3]['post_count']
    for run in runs:
        for topic in run['topics']:
            assert topic['summary'] and topic['evidence'] and topic['authors']
            assert 0<=topic['score']<=100
            assert topic['score']==round(sum(topic['factors'][k]*topic['weights'][k] for k in WEIGHTS if topic['factors'][k] is not None),1)
            assert all(p['provenance']=='synthetic' for p in topic['evidence'])
        top=[t for t in run['topics'] if t['top']]
        assert 1<=len(top)<=3 and all(t['recommended'] for t in top)
        assert all('football' not in t['title'].lower() for t in top)


def test_account_filter_and_persistence(client):
    handles=[a['handle'] for a in client.get('/api/state').json()['accounts']]
    for handle in handles:
        assert client.post('/api/accounts',json={'handle':handle,'enabled':False}).status_code==200
    assert analysis(client)['topics']==[]
    client.post('/api/accounts',json={'handle':handles[0],'enabled':True})
    run=analysis(client)
    assert run['account_count']==1
    assert all(t['authors']==[handles[0]] for t in run['topics'])
    client.delete('/api/accounts/'+handles[0])
    assert all(a['handle']!=handles[0] for a in client.get('/api/state').json()['accounts'])
    db.init()
    assert all(a['handle']!=handles[0] for a in client.get('/api/state').json()['accounts'])


def post(id='p1',hours=.5,**kwargs):
    return dict(id=id,handle='real_source',text='AI agents need human approval and growth marketing review.',
        created_at=(datetime.now(timezone.utc)-timedelta(hours=hours)).isoformat(),**kwargs)


def test_import_window_provenance_validation_and_upsert(client):
    assert client.post('/api/import',json={'posts':[post(),post('old',hours=3)]}).status_code==200
    assert client.post('/api/import',json={'posts':[post()]}).status_code==200
    assert client.get('/api/state').json()['imported_posts']==2
    recent=client.post('/api/analyze',json={'hours':1,'mode':'imported'}).json()
    wider=client.post('/api/analyze',json={'hours':4,'mode':'imported'}).json()
    assert recent['post_count']==1 and wider['post_count']==2
    assert all(p['provenance']=='imported' for t in recent['topics'] for p in t['evidence'])
    bad=post('bad',likes=-1)
    assert client.post('/api/import',json={'posts':[post('new'),bad]}).status_code==422
    assert client.get('/api/state').json()['imported_posts']==2  # atomic, no partial new row
    for invalid in [post('bad',hours=-24),{**post(),'created_at':'2026-01-01T00:00:00'}]:
        assert client.post('/api/import',json={'posts':[invalid]}).status_code==422


def test_draft_angles_review_approval_edit_and_export(client):
    d=make_draft(client)
    assert len(d['angles'])==3 and len({a['type'] for a in d['angles']})==3
    assert 1<=len(d['text'])<=280 and 'no LLM' in d['provider']
    assert client.get(f"/api/drafts/{d['id']}/export").status_code==409
    path=f"/api/drafts/{d['id']}"
    assert client.put(path,json={'text':'A useful signal deserves a customer question. What would you test?'}).status_code==200
    approved=client.post(path+'/approve').json()
    assert approved['status']=='approved' and approved['approved_at']
    assert client.get(path+'/export').text==approved['text']
    # Approval persists across requests, but must never survive changed text.
    assert any(x['status']=='approved' for x in client.get('/api/state').json()['drafts'])
    assert client.put(path,json={'text':'A changed perspective needs fresh review.'}).json()['status']=='draft'
    assert client.get(path+'/export').status_code==409


def test_invalid_inputs_and_missing_records(client):
    for text in ['', ' ', 'x'*281, 'Visit https://example.com', '你好']:
        d=make_draft(client)
        assert client.put('/api/drafts/'+d['id'],json={'text':text}).status_code==422
    assert client.post('/api/analyze',json={'hours':3,'mode':'demo'}).status_code==422
    assert client.post('/api/analyze',json={'hours':4,'mode':'streaming'}).status_code==422
    assert client.post('/api/accounts',json={'handle':'<script>'}).status_code==422
    assert client.get('/api/drafts/missing/export').status_code==404
    assert client.post('/api/drafts',json={'analysis_id':'missing','topic_id':'0'}).status_code==404


def test_brand_keywords_change_recommendations(client):
    response=client.put('/api/brief',json={'positioning':'Sports editorial','audience':'Football fans','keywords':['football']})
    assert response.status_code==200
    run=analysis(client)
    assert 'football' in run['topics'][0]['title'].lower()
    assert run['topics'][0]['top']
    assert client.put('/api/brief',json={'positioning':'Valid brief','audience':'Teams','keywords':[' ']}).status_code==422


def test_empty_vocabulary_and_unknown_baseline():
    p=dict(id='p',handle='a',text='and the or',created_at=CLOCK.isoformat(),likes=0,reposts=0,replies=0)
    assert detect([p],[],CLOCK,4,DEFAULT_BRIEF)==[]
    p['text']='AI agents support human approval for marketing'
    topics=detect([p,p],[],CLOCK,4,DEFAULT_BRIEF)
    assert len(topics)==1 and len(topics[0]['evidence'])==1
    assert topics[0]['momentum'] is None and topics[0]['factors']['momentum'] is None and topics[0]['weights']['momentum']==0


def test_ui_assets_served_locally(client):
    assert 'TelyClaw' in client.get('/').text
    for path in ['/static/style.css','/static/app.js']:
        assert client.get(path).status_code==200


def test_provider_failure_is_explicit(client, monkeypatch):
    import app.main as main
    def fail(*args):
        raise RuntimeError('private provider details')
    monkeypatch.setattr(main,'generate',fail)
    run=analysis(client)
    r=client.post('/api/drafts',json={'analysis_id':run['id'],'topic_id':run['topics'][0]['id']})
    assert r.status_code==502 and 'private' not in r.text
