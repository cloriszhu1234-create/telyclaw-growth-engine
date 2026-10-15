"""Synthetic, test-only paraphrases; no real imported dataset is required."""
from datetime import datetime, timedelta, timezone
import pytest
from app.semantics import concept_evidence
from app.trends import detect,DEFAULT_BRIEF

NOW=datetime.now(timezone.utc)

def post(text,i,handle=None,age=.2,metrics=True):
    return dict(id=str(i),handle=handle or f'fixture_{i}',text=text,created_at=(NOW-timedelta(hours=age)).isoformat(),
                likes=10 if metrics else None,reposts=2 if metrics else None,replies=1 if metrics else None,provenance='test_only')

@pytest.mark.parametrize('theme,texts',[
 ('orchestration',['Coordinating specialist workers needs clear ownership of every handoff.', 'Multi-agent systems should route tasks between specialists with explicit state.']),
 ('interoperability',['Agent interoperability lets different runtimes exchange tasks.', 'Cross-framework tool connectors need a common protocol.']),
 ('coding',['Coding assistants shorten feedback cycles when engineers verify changes.', 'Codex and Claude Code should run checks before committing software.']),
 ('oversight',['Human-in-the-loop keeps consequential decisions accountable.', 'Agent oversight requires approval gates before actions.']),
 ('context',['Context efficiency matters more than adding tokens blindly.', 'Compressing memory helps keep long-running tasks within token budgets.']),
])
def test_paraphrases_share_specific_theme_without_shared_keywords(theme,texts):
    rows=[post(t,i) for i,t in enumerate(texts)]
    result=detect(rows,[],NOW,168,DEFAULT_BRIEF)
    assert len(result)==1,[(t['title'],[p['id'] for p in t['evidence']]) for t in result]
    t=result[0]
    assert t['theme']==theme
    assert len(t['authors'])==2 and t['confirmation']=='multi_source'
    assert t['theme_labels']['zh'] and t['theme_labels']['en']==t['title']
    assert all(p['text']==texts[i] for i,p in enumerate(rows))
    assert len(t['concept_evidence'])==2
    assert all(p['handle'] in t['summary'] for p in rows)


def test_generic_agent_ai_workflow_cannot_merge_different_themes():
    texts=['AI agent workflow: use context compression to reduce token budgets.',
           'AI agent workflow: agent interoperability needs cross-framework protocols.',
           'AI agent workflow: human oversight needs approval gates.',
           'AI agent workflow: a coding assistant runs compiler tests.',
           'AI agent workflow: multi-agent orchestration coordinates specialists.',
           'AI agent workflow: internal logic is completely different.']
    result=detect([post(t,i) for i,t in enumerate(texts)],[],NOW,4,DEFAULT_BRIEF)
    assert len(result)==len(texts)
    assert not any(t['title'] in ['Internal Logic & Completely Different','Agent Expected & Agentfeedback True'] for t in result)
    assert concept_evidence('AI agents and agentic AI workflows are interesting.')=={}


def test_same_author_is_not_independent_and_missing_is_not_zero():
    texts=['Multi-agent orchestration needs reliable task ownership.', 'Coordinating multiple agents requires clear recovery rules.']
    result=detect([post(texts[0],0,'Alice',metrics=False),post(texts[1],1,'alice',metrics=False)],[],NOW,4,DEFAULT_BRIEF)[0]
    assert result['authors']==['alice'] and result['confirmation']=='single_source'
    assert result['available_engagement'] is None
    assert result['factors']['engagement'] is None and result['weights']['engagement']==0
    assert result['momentum'] is None and result['weights']['momentum']==0
    assert sum(result['weights'].values())==pytest.approx(1)


def test_result_count_is_evidence_driven_and_order_reproducible():
    texts=['Context management reduces token waste.', 'Memory compression keeps token budgets small.',
           'Human-in-the-loop should guard irreversible actions.', 'Human oversight adds accountability.',
           'Regional rainfall changes alpine snowpack measurements.']
    rows=[post(t,i) for i,t in enumerate(texts)]
    first=detect(rows,[],NOW,4,DEFAULT_BRIEF)
    second=detect(list(reversed(rows)),[],NOW,4,DEFAULT_BRIEF)
    assert {frozenset(p['id'] for p in t['evidence']) for t in first}=={frozenset(p['id'] for p in t['evidence']) for t in second}
    assert len(detect(rows[:2],[],NOW,4,DEFAULT_BRIEF))==1
    assert len(first)==3
    assert len(detect(rows+[post('Agent interoperability connects runtime frameworks.',8)],[],NOW,4,DEFAULT_BRIEF))==4


def test_specific_editorial_fit_ranks_above_generic_ai_signal():
    rows=[post('AI agents are completely different and exciting.',0),
          post('Context management cuts unnecessary tokens in production.',1),
          post('Memory compression protects token budgets for long tasks.',2)]
    result=detect(rows,[],NOW,4,DEFAULT_BRIEF)
    assert result[0]['theme']=='context'
    assert result[0]['factors']['relevance']>result[1]['factors']['relevance']


def test_broad_multi_agent_phrase_does_not_override_conflicting_specific_concerns():
    rows=[post('Multi-agent context compression reduces token budgets.',0),
          post('Multi-agent human oversight requires approval gates.',1)]
    result=detect(rows,[],NOW,4,DEFAULT_BRIEF)
    assert len(result)==2
    assert {t['theme'] for t in result}=={'context','oversight'}
