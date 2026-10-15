"""Test-only discussions; not quotations from the user's real imported posts."""
import copy
import hashlib
import pytest
from app.semantics import CONCEPTS
from app.topic_quality import presentation
from app.trends import DEFAULT_BRIEF,detect,normalized
from test_semantic_topics import NOW,post

CODING_DISCUSSIONS = [
    'A coding agent needs error feedback to recover from failed changes.',
    'A programming agent should troubleshoot failures with tests and verification.',
    'A coding assistant needs context compression for better token efficiency.',
    'A coding agent harness can execute complex software engineering tasks.',
]


def test_engineering_name_and_cited_insight_are_evidence_conditioned():
    rows=[post(text,i) for i,text in enumerate(CODING_DISCUSSIONS)]
    before=copy.deepcopy(rows)
    topics=detect(rows,[],NOW,168,DEFAULT_BRIEF)
    assert len(topics)==1
    t=topics[0]
    assert t['title']=='Engineering & Reliability of AI Coding Agents'
    assert t['theme_labels']['zh']=='AI 编程智能体的工程化与可靠性'
    assert '4 of 4' in t['shared_insight']['en']
    assert '不代表行业共识或讨论量正在加速' in t['shared_insight']['zh']
    assert {c['facet'] for c in t['insight_support']}=={'feedback','validation','context','execution'}
    for concern in t['insight_support']:
        for row in concern['sources']:
            original=next(p for p in rows if p['id']==row['post_id'])
            assert row['handle']==original['handle']
            assert all(match in original['text'].lower() for match in row['matches'])
            assert '@'+row['handle'] in t['shared_insight']['en']
    assert rows==before
    # Existing topic/publication rollup identity is retained despite display rename.
    assert t['topic_key']==hashlib.sha256(normalized(CONCEPTS['coding'][0]).encode()).hexdigest()[:20]
    assert t['momentum'] is None and t['factors']['momentum'] is None and t['weights']['momentum']==0
    assert t['momentum_status']=='Insufficient historical data'


def test_names_do_not_depend_on_specific_handles_products_or_group_size():
    for size in (2,3,4):
        rows=[post(text,i,'other_'+str(i)) for i,text in enumerate(CODING_DISCUSSIONS[:size])]
        result=presentation('coding',rows)
        assert result['labels']['zh']=='AI 编程智能体的工程化与可靠性'
    broad=presentation('coding',[post('A coding assistant can write a program.',0),post('A programming agent generates software.',1)])
    assert broad['labels']['en']==CONCEPTS['coding'][0]


@pytest.mark.parametrize('text',[
    'Communication protocols let autonomous agents exchange messages across runtimes.',
    'AI Agent interoperability requires shared message formats.',
    'Agents communicate across systems using messaging protocols.',
])
def test_clear_protocol_singleton_is_named_and_remains_a_single_signal(text):
    t=detect([post(text,0)],[],NOW,4,DEFAULT_BRIEF)[0]
    assert t['theme_labels']['zh']=='AI Agent 互操作性与通信协议'
    assert t['confirmation']=='single_source'
    assert t['evidence'][0]['text']==text
    assert t['insight_support'][0]['facet']=='protocols'
    assert t['momentum'] is None


@pytest.mark.parametrize('text',[
    'Protocol updates are coming soon; more information next week.',
    'Network protocol transport uses encrypted packets between services.',
    'AI agents are interesting and surprisingly different.',
])
def test_ambiguous_singletons_stay_unconfirmed(text):
    t=detect([post(text,0)],[],NOW,4,DEFAULT_BRIEF)[0]
    assert t['title']=='Unconfirmed Single-Post Signal'
    assert t['theme_labels']['zh']=='待确认的单帖信号'
    assert t['insight_support']==[]
    assert '待确认' in t['shared_insight']['zh']


def test_one_detailed_post_cannot_supply_a_group_wide_engineering_claim():
    rows=[post('A coding assistant needs error feedback, tests and context compression.',0),
          post('A programming agent creates software.',1),
          post('Coding assistants write code.',2)]
    result=presentation('coding',rows)
    assert result['labels']['en']==CONCEPTS['coding'][0]
    assert '1 of 3' in result['insight']['en']


def test_feedback_only_name_does_not_invent_test_evidence():
    result=presentation('coding',[post('A coding agent needs error feedback.',0)])
    assert result['labels']['en']=='Feedback & Error Recovery for AI Coding Agents'
    assert 'validation' not in result['labels']['en'].lower()


def test_presentation_does_not_change_membership_scores_or_momentum(monkeypatch):
    import app.trends as trends
    rows=[post(text,i) for i,text in enumerate(CODING_DISCUSSIONS)]
    current=detect(rows,[],NOW,4,DEFAULT_BRIEF)[0]
    monkeypatch.setattr(trends,'presentation',lambda theme,rows,fallback=None:{'labels':{'en':CONCEPTS[theme][0],'zh':CONCEPTS[theme][1]},'insight':{},'support':[]})
    original=detect(rows,[],NOW,4,DEFAULT_BRIEF)[0]
    for key in ['evidence','authors','score','factors','weights','momentum','momentum_status','topic_key']:
        assert current[key]==original[key]


# Relevant user-supplied source excerpts. Claims (including 98%) are unverified;
# this is an isolated regression fixture, never demo data or a live fetch.
CONTEXT_OUTPUT_EXCERPT = (
    'Someone built a plugin that cuts up to 98% of the tokens your coding agent burns on tool output. '
    'Normally every log, snapshot and API response lands in your agent’s context. '
    'Context Mode runs them in a sandbox and passes on only the result. '
    'It also logs your session, so after compaction the agent finds what it needs instead of starting blind.'
)


def test_tool_output_compaction_source_contributes_to_shared_insight():
    rows=[post(t,i) for i,t in enumerate(CODING_DISCUSSIONS)]
    rows[2]['text']=CONTEXT_OUTPUT_EXCERPT
    before=copy.deepcopy(rows)
    t=detect(rows,[],NOW,168,DEFAULT_BRIEF)[0]
    assert len(t['evidence'])==4
    assert '4 of 4' in t['shared_insight']['en']
    assert '所选 4 条帖子中，4 条' in t['shared_insight']['zh']
    concern=next(c for c in t['insight_support'] if c['facet']=='context')
    assert concern['sources']==[{'post_id':'2','handle':'fixture_2','matches':['compaction','tool output']}]
    assert all(match in rows[2]['text'].lower() for match in concern['sources'][0]['matches'])
    assert all('98' not in text for text in t['shared_insight'].values())
    assert t['momentum'] is None and t['weights']['momentum']==0
    assert rows==before


@pytest.mark.parametrize('text,expected',[
    ('A coding agent filters tool output before it enters context.', 'tool output'),
    ('The assistant preserves context after compaction.', 'compaction'),
    ('A coding assistant compresses tool outputs for the context window.', 'tool outputs'),
    ('A coding agent reduces context with tool-output filtering.', 'tool-output'),
    ('A coding agent uses context compaction during long tasks.', 'context compaction'),
    ('Coding agents should use tokens efficiently within token budgets.', 'tokens efficiently'),
])
def test_general_context_efficiency_phrasing_not_product_or_author_rules(text,expected):
    from app.topic_quality import context_matches
    assert expected in context_matches(text.lower())


@pytest.mark.parametrize('text',[
    'Soil compaction improves the road foundation.',
    'The terminal records tool output from a weather script.',
    'A coding agent writes a program.',
    'This context explains local history; the discussion includes no model.',
    'Authentication tokens in the login prompt appear in tool output.',
])
def test_ambiguous_compaction_or_tool_output_is_not_context_efficiency(text):
    from app.topic_quality import context_matches
    assert context_matches(text.lower())==[]
