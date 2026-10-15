"""Test-only discussions and real calculation expectations, not actual social results."""
from datetime import datetime, timedelta, timezone
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.trends import DEFAULT_BRIEF, detect
from app.content import generate
from app import db
from app.publishing import calculations, aggregate

NOW=datetime.now(timezone.utc)
DISCUSSIONS=[
    'Multi-agent orchestration needs reliable tool handoffs and shared state between specialist agents.',
    'Coordinating multiple agents requires shared memory and reliable tool routing across workers.',
    'Agent teams fail without coordination, shared state and clear tool handoff ownership.',
    'AI programming assistants can generate code but software engineers still review security vulnerabilities.',
    'Coding assistants should test generated software for security flaws before developer approval.',
    'Developers need secure code evaluation when programming assistants produce vulnerable software.',
    'Content attribution should connect product clicks to qualified buyer replies instead of raw impressions.',
    'Marketing analytics needs qualified engagement and product click attribution, not vanity reach.',
    'Measuring content outcomes means qualified replies, product clicks and audience quality.'
]


def source(text,i,age=.5,**changes):
    return dict(id=str(i),handle='test_author_'+str(i),text=text,created_at=(NOW-timedelta(hours=age)).isoformat(),
                likes=10,reposts=2,replies=1,provenance='test_only',**changes)


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'growth.db'))
    with TestClient(app) as c:yield c


def draft(c):
    run=c.post('/api/analyze',json={'hours':4,'mode':'demo'}).json()
    r=c.post('/api/drafts',json={'analysis_id':run['id'],'topic_id':run['topics'][0]['id']})
    assert r.status_code==200,r.text
    return r.json()


def publish(c,d=None,id='400001',age=1):
    d=d or draft(c)
    c.post('/api/drafts/'+d['id']+'/approve')
    r=c.post('/api/drafts/'+d['id']+'/publish',json={'url':f'https://x.com/my_brand/status/{id}',
        'published_at':(datetime.now(timezone.utc)-timedelta(minutes=age)).isoformat()})
    assert r.status_code==201,r.text
    return r.json()


def test_related_discussions_cluster_without_sample_specific_assignments():
    rows=[source(t,i) for i,t in enumerate(DISCUSSIONS)]
    topics=detect(rows,[],NOW,168,DEFAULT_BRIEF)
    groups=[{p['id'] for p in t['evidence']} for t in topics]
    assert len(topics)<len(rows)
    for expected in [{'0','1','2'},{'3','4','5'},{'6','7','8'}]:
        assert any(expected<=g for g in groups),groups
    assert all(not ({'0','3'}<=g or {'0','6'}<=g or {'3','6'}<=g) for g in groups),groups
    assert len(topics)==3,[(t['title'],g) for t,g in zip(topics,groups)]
    for t in topics:
        assert len(t['authors'])==3 and len(t['discussion_points'])==3
        assert all(p['handle'] in t['summary'] for p in t['evidence'])
        assert t['momentum'] is None and t['weights']['momentum']==0
        assert t['momentum_status']=='Insufficient historical data'
        assert t['available_engagement']==39
        assert t['why_trending'] and t['why_care'] and t['content_move']
        angles,text,provider=generate(t,DEFAULT_BRIEF)
        assert len(angles)==3 and all(t['title'].lower() in a['idea'].lower() for a in angles)
        assert all(text!=p['text'] for p in t['evidence']) and len(text)<=280
        assert 'no LLM' in provider


def test_unrelated_singleton_is_not_forced_into_larger_topic():
    rows=[source(DISCUSSIONS[0],0),source(DISCUSSIONS[1],1),source('Volcanic eruptions threaten island aviation with ash clouds.',2)]
    topics=detect(rows,[],NOW,4,DEFAULT_BRIEF)
    assert any(len(t['evidence'])==1 and t['evidence'][0]['id']=='2' for t in topics)
    assert any(len(t['evidence'])==2 for t in topics)


def test_velocity_requires_sufficient_spread_authors_and_baseline():
    current=[source(DISCUSSIONS[i%3]+f' experiment {i}',i,age=age) for i,age in enumerate([.1,.8,1.8,2.8,3.8])]
    previous=[source(DISCUSSIONS[i%3]+f' baseline {i}',i+10,age=age) for i,age in enumerate([4.2,5.8,7.5])]
    topics=detect(current,previous,NOW,4,DEFAULT_BRIEF)
    assert len(topics)==1
    assert topics[0]['momentum']==pytest.approx(66.7)
    assert topics[0]['factors']['momentum']>0
    small=detect(current,previous[:1],NOW,4,DEFAULT_BRIEF)[0]
    assert small['momentum'] is None and small['weights']['momentum']==0
    one_author=[{**p,'handle':'same_source'} for p in previous]
    assert detect(current,one_author,NOW,4,DEFAULT_BRIEF)[0]['momentum'] is None


def test_single_viral_post_has_damped_engagement_quality():
    one=source(DISCUSSIONS[0],0);one['likes']=1000000
    t=detect([one],[],NOW,4,DEFAULT_BRIEF)[0]
    assert t['factors']['engagement']<=33.4
    assert t['factors']['breadth']==20
    assert 'Single-account' in t['why_trending']


def test_topic_specific_drafts_differ_and_no_product_capability_is_assumed():
    topics=detect([source(t,i) for i,t in enumerate(DISCUSSIONS)],[],NOW,4,DEFAULT_BRIEF)
    outputs=[generate(t,DEFAULT_BRIEF) for t in topics]
    assert len({o[1] for o in outputs})==len(topics)
    assert all('No additional product capabilities' in t['why_care'] for t in topics)
    assert all('Provisional positioning' in o[0][2]['idea'] for o in outputs)


def test_empty_performance_is_honest(client):
    value=client.get('/api/performance').json()
    assert value['posts']==[] and value['topics']==[]
    assert value['aggregate']['total_engagement'] is None
    assert value['aggregate']['engagement_rate'] is None
    assert all(v is None for v in value['aggregate']['totals'].values())


def test_composer_approval_encoding_and_no_publication_side_effect(client):
    d=draft(client);path='/api/drafts/'+d['id']
    assert client.get(path+'/composer',follow_redirects=False).status_code==409
    text='Agent orchestration: test handoffs & ownership. What changes for buyers? #Growth'
    client.put(path,json={'text':text});client.post(path+'/approve')
    r=client.get(path+'/composer',follow_redirects=False)
    assert r.status_code==303
    url=urlsplit(r.headers['location'])
    assert url.scheme=='https' and url.netloc=='twitter.com' and url.path=='/intent/tweet'
    assert parse_qs(url.query)['text']==[text]
    assert client.get('/api/performance').json()['posts']==[]
    client.put(path,json={'text':'Changed text requires fresh approval.'})
    assert client.get(path+'/composer',follow_redirects=False).status_code==409


def test_publish_snapshot_duplicates_lock_and_export(client):
    d=draft(client);path='/api/drafts/'+d['id']
    body={'url':'https://twitter.com/My_Brand/status/500001?s=20','published_at':(NOW-timedelta(minutes=1)).isoformat()}
    assert client.post(path+'/publish',json=body).status_code==409
    client.post(path+'/approve')
    pub=client.post(path+'/publish',json=body).json()
    assert pub['url']=='https://x.com/my_brand/status/500001'
    assert client.post(path+'/publish',json=body).status_code==409
    other=draft(client);client.post('/api/drafts/'+other['id']+'/approve')
    assert client.post('/api/drafts/'+other['id']+'/publish',json=body).status_code==409
    assert client.get(path+'/export').text==d['text']
    assert client.put(path,json={'text':'Overwrite attempt'}).status_code==409
    assert client.post(path+'/approve').json()['status']=='published'
    revision=client.post(path+'/revision').json()
    assert revision['id']!=d['id'] and revision['status']=='draft'
    assert 'published_url' not in revision
    assert client.get('/api/performance').json()['posts'][0]['text']==d['text']


@pytest.mark.parametrize('url',['http://x.com/a/status/123','https://x.com.evil.example/a/status/123','javascript:alert(1)','https://x.com/a/status/nope','https://x.com/a/status/0'])
def test_publication_url_validation(client,url):
    d=draft(client);client.post('/api/drafts/'+d['id']+'/approve')
    r=client.post('/api/drafts/'+d['id']+'/publish',json={'url':url,'published_at':(NOW-timedelta(minutes=1)).isoformat()})
    assert r.status_code==422


def test_measurement_updates_history_and_aggregate(client):
    p=publish(client)
    path='/api/publications/'+p['id']+'/measurements'
    first={'measured_at':(datetime.now(timezone.utc)-timedelta(seconds=30)).isoformat(),'impressions':1000,'likes':10,'reposts':2,'replies':3,'bookmarks':5}
    assert client.post(path,json=first).status_code==201
    second={**first,'measured_at':datetime.now(timezone.utc).isoformat(),'likes':20}
    assert client.post(path,json=second).status_code==201
    value=client.get('/api/performance').json()
    assert value['aggregate']['total_engagement']==30  # latest snapshot, not 20 + 30
    assert value['aggregate']['engagement_rate']==3
    assert value['topics'][0]['total_engagement']==30
    assert len(value['posts'][0]['snapshots'])==2
    assert value['posts'][0]['metrics']['attributed_followers'] is None
    assert client.post(path,json=first).status_code==409
    with TestClient(app) as restarted:
        assert restarted.get('/api/performance').json()['aggregate']['total_engagement']==30


def test_partial_unknown_and_zero_calculations():
    assert calculations({})['total_engagement'] is None
    assert calculations({'likes':0})['total_engagement']==0
    assert calculations({'likes':5,'impressions':0})['engagement_rate'] is None
    partial=calculations({'likes':5,'impressions':100})
    assert partial['engagement_rate']==5 and not partial['engagement_complete']
    posts=[{'metrics':{'likes':10,'impressions':100},'calculated':calculations({'likes':10,'impressions':100})},
           {'metrics':{'likes':90},'calculated':calculations({'likes':90})}]
    a=aggregate(posts)
    assert a['total_engagement']==100 and a['engagement_rate']==10 and a['rate_posts']==1
    assert not a['engagement_complete']
    assert a['totals']['profile_visits'] is None


def test_metrics_validation_and_attribution_guard(client):
    p=publish(client);path='/api/publications/'+p['id']+'/measurements'
    now=datetime.now(timezone.utc).isoformat()
    for bad in [{'likes':-1},{'likes':True},{'attributed_followers':2},
                {'measured_at':(NOW+timedelta(days=1)).isoformat()},
                {'measured_at':(NOW-timedelta(days=2)).isoformat()}, {'measured_at':'2026-01-01T00:00:00'}]:
        assert client.post(path,json={'measured_at':now,**bad}).status_code==422
    assert client.post(path,json={'measured_at':now,'attributed_followers':2,'attribution_evidence':'Post-level attributed-follows report supplied by the user.'}).status_code==201
    value=client.get('/api/performance').json()['aggregate']
    assert value['totals']['attributed_followers']==2 and value['total_engagement'] is None


def test_same_topic_aggregate_and_existing_records_preserved(client):
    a=publish(client,id='600001');b=publish(client,id='600002')
    assert a['topic_key']==b['topic_key']
    for p in (a,b):
        client.post('/api/publications/'+p['id']+'/measurements',json={'measured_at':datetime.now(timezone.utc).isoformat(),'likes':3})
    result=client.get('/api/performance').json()
    assert result['topics'][0]['posts']==2 and result['topics'][0]['total_engagement']==6
    before=client.get('/api/state').json()
    db.init()
    assert client.get('/api/state').json()==before


def test_optional_llm_is_labeled_validated_and_copying_is_rejected(monkeypatch):
    import httpx
    import app.content as content
    topic=detect([source(t,i) for i,t in enumerate(DISCUSSIONS[:3])],[],NOW,4,DEFAULT_BRIEF)[0]
    local_angles,_,_=generate(topic,DEFAULT_BRIEF)
    original_client=httpx.Client
    value={'angles':local_angles,'text':'Agent orchestration needs a measurable handoff contract. Test recovery before increasing autonomy.'}
    def response(request):
        return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(value)}}]})
    monkeypatch.setenv('OPENAI_API_KEY','non-secret-test-placeholder')
    monkeypatch.setattr(content.httpx,'Client',lambda **kwargs:original_client(transport=httpx.MockTransport(response)))
    assert 'LLM' in generate(topic,DEFAULT_BRIEF)[2]
    value['text']=DISCUSSIONS[0]
    with pytest.raises(ValueError,match='copied'):
        generate(topic,DEFAULT_BRIEF)
    value['text']='A short original post'
    value['angles']=value['angles'][:2]
    with pytest.raises(ValueError):generate(topic,DEFAULT_BRIEF)


def test_unknown_post_metrics_are_never_synthesized_and_time_validation(client):
    d=draft(client);client.post('/api/drafts/'+d['id']+'/approve')
    for timestamp in ['2026-01-01T00:00:00',(NOW+timedelta(days=1)).isoformat()]:
        assert client.post('/api/drafts/'+d['id']+'/publish',json={'url':'https://x.com/test/status/123456','published_at':timestamp}).status_code==422
    p=publish(client,d)
    assert client.get('/api/performance').json()['posts'][0]['calculated']['total_engagement'] is None
    path='/api/publications/'+p['id']+'/measurements'
    assert client.post(path,json={'measured_at':datetime.now(timezone.utc).isoformat()}).status_code==201
    result=client.get('/api/performance').json()
    assert result['aggregate']['measured_posts']==0
    assert result['aggregate']['total_engagement'] is None
    assert result['aggregate']['engagement_rate'] is None
