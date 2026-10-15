"""Test-only source subjects. No live account data, API calls or seeded records."""
import copy
import pytest
from app.trends import DEFAULT_BRIEF, detect
from app.topic_quality import singleton_subject
from test_semantic_topics import NOW, post


@pytest.mark.parametrize('text,en,zh',[
    ('You do not need every AI Agent to use the same framework.',
     'AI Agent Framework Selection', 'AI Agent 的框架选择'),
    ('Different frameworks can power agents in the same project.',
     'AI Agent Framework Selection', 'AI Agent 的框架选择'),
    ('An engineer shares a template: this prompt helps an engineering lead plan the work.',
     'Prompt Templates for Engineering Leadership', '工程管理场景的提示词模板'),
    ('A technical leader shares prompt templates for engineering managers.',
     'Prompt Templates for Engineering Leadership', '工程管理场景的提示词模板'),
    ('A prompt template helps structure a customer research question.',
     'Prompt Design & Templates', '提示词设计与模板'),
    ('Try changing the prompt for your language model before accepting the answer.',
     'AI Prompt Design', 'AI 提示词设计'),
])
def test_single_source_subject_is_named_and_evidence_remains_weak(text,en,zh):
    row=post(text,0,metrics=False)
    before=copy.deepcopy(row)
    t=detect([row],[],NOW,168,DEFAULT_BRIEF)[0]
    assert t['theme_labels']=={'en':en,'zh':zh}
    assert t['title']==en and t['confirmation']=='single_source'
    assert t['momentum'] is None and t['factors']['momentum'] is None
    assert t['available_engagement'] is None and t['weights']['engagement']==0
    assert t['momentum_status']=='Insufficient historical data'
    assert 'not independent confirmation' in t['shared_insight']['en']
    assert '已验证效果' in t['shared_insight']['zh']
    assert row==before
    for concern in t['insight_support']:
        for source in concern['sources']:
            assert source['handle']==row['handle']
            assert all(match in text.lower() for match in source['matches'])


def test_framework_choice_does_not_invent_protocol_or_shared_runtime_claims():
    t=detect([post('You do not need every AI Agent to use the same framework.',0)],[],NOW,168,DEFAULT_BRIEF)[0]
    assert 'protocol' not in t['title'].lower()
    assert t['theme'] is None  # presentation title earns no new relevance credit
    assert t['relevance_evidence']['domain_fit'] is False
    assert t['factors']['relevance']==10
    assert t['insight_support'][0]['facet']=='subject'


@pytest.mark.parametrize('text',[
    'Local rainfall changes the alpine snowpack.',
    'The terminal prompt uses a template for file paths.',
    'Protocol. Internal logic is completely different.',
    'A compiler refresh introduced a new diagnostic format.',
])
def test_unclassified_text_has_an_explicit_source_excerpt_title(text):
    t=detect([post(text,0)],[],NOW,4,DEFAULT_BRIEF)[0]
    assert t['title'].startswith('Source topic: “')
    assert t['theme_labels']['zh'].startswith('原帖议题：「')
    assert 'Unconfirmed Single-Post Signal' not in t['title']
    assert t['confirmation']=='single_source' and t['momentum'] is None
    assert t['insight_support']==[]
    assert 'title quotes the source text' in t['shared_insight']['en']


def test_handles_links_and_distant_words_cannot_supply_a_named_subject():
    row=post('A local update. https://example.test/ai-agent-framework/prompt-template',0,'ai_agents')
    names,support=singleton_subject(row)
    assert names['en']=='Source topic: “A local update”' and not support
    distant=post('Agents work here. '+('unrelated background '*30)+'A framework is announced.',1)
    assert singleton_subject(distant)[0]['en'].startswith('Source topic:')


def test_unknown_excerpt_is_bounded_and_source_text_is_not_rewritten():
    text='Unclassified measurement ' + ('unusually detailed evidence '*80)
    row=post(text,0)
    names,support=singleton_subject(row)
    assert len(names['en'])<100 and names['en'].endswith('…”')
    assert row['text']==text and not support


@pytest.mark.parametrize('text',[
    'You do not need every AI Agent to use the same framework.',
    'Here is a prompt template for an engineering lead to organize decisions.',
    'Volcanic ash changes the flight plan.',
])
def test_subject_naming_cannot_change_membership_scoring_or_rollup_keys(text,monkeypatch):
    import app.trends as trends
    rows=[post(text,0)]
    current=detect(rows,[],NOW,168,DEFAULT_BRIEF)[0]
    monkeypatch.setattr(trends,'presentation',lambda theme,rows,fallback=None:{
        'labels':{'en':'Unconfirmed Single-Post Signal','zh':'待确认的单帖信号'},
        'insight':{},'support':[]})
    previous=detect(rows,[],NOW,168,DEFAULT_BRIEF)[0]
    for key in ['evidence','authors','score','factors','weights','rank','top','recommended',
                'momentum','momentum_status','topic_key','theme','relevance_evidence']:
        assert current[key]==previous[key]


def test_named_singletons_stay_separate_from_multi_source_coding_cluster():
    from test_topic_quality import CODING_DISCUSSIONS
    texts=CODING_DISCUSSIONS+[
        'You do not need every AI Agent to use the same framework.',
        'This prompt template helps an engineering lead structure a planning session.',
    ]
    rows=[post(text,i) for i,text in enumerate(texts)]
    result=detect(rows,[],NOW,168,DEFAULT_BRIEF)
    groups={frozenset(p['id'] for p in t['evidence']):t for t in result}
    assert set(groups)=={frozenset({'0','1','2','3'}),frozenset({'4'}),frozenset({'5'})}
    assert groups[frozenset({'4'})]['title']=='AI Agent Framework Selection'
    assert groups[frozenset({'5'})]['title']=='Prompt Templates for Engineering Leadership'
    assert groups[frozenset({'0','1','2','3'})]['title']=='Engineering & Reliability of AI Coding Agents'
