"""Versioned local domain vocabulary. No sample IDs, cluster quotas or remote models.

Concepts require specific phrases/context; AI, agent and workflow alone never
establish a shared theme. This is a reproducible heuristic, not embeddings.
"""
import re
from collections import Counter

CONCEPTS = {
    'orchestration': ('Multi-Agent Orchestration', '多智能体协作与编排', [
        r'\bmulti[ -]?agent\b', r'\bmultiple agents?\b', r'\bagent teams?\b',
        r'\borchestrat\w*\b', r'\bcoordinat\w*\b', r'\btool (?:handoffs?|routing)\b',
        r'\b(?:specialist|worker) agents?\b']),
    'interoperability': ('Agent Frameworks & Interoperability', '智能体框架与互操作性', [
        r'\bagent frameworks?\b', r'\bagent interoperab\w*\b', r'\b(?:a2a|mcp)\b',
        r'\bmodel context protocol\b', r'\b(?:cross[ -]framework|agent[ -]to[ -]agent)\b',
        r'\b(?:tool|agent) (?:protocols?|connectors?)\b']),
    'coding': ('Agent-Assisted Coding Workflows', '智能体辅助编程工作流', [
        r'\b(?:coding|programming|code) (?:agents?|assistants?|workflows?)\b',
        r'\b(?:claude code|codex|cursor|copilot)\b', r'\b(?:agentic|vibe) coding\b',
        r'\b(?:agents?|assistants?)\b.{0,45}\b(?:generate|write|debug|review)\w* (?:code|software)\b']),
    'oversight': ('Human Oversight of Agents', '智能体的人工监督与审核', [
        r'\bhuman[ -]in[ -]the[ -]loop\b', r'\bhuman (?:oversight|approval|review|supervision|judgment)\b',
        r'\b(?:agent|autonomous)\w*\b.{0,45}\b(?:guardrails?|approval gates?|supervision)\b',
        r'\b(?:approval gates?|human checkpoints?|agent oversight)\b']),
    'context': ('Context & Memory Efficiency', '上下文与记忆效率', [
        r'\bcontext (?:management|efficien\w*|windows?|compression|engineering|rot|budget\w*)\b',
        r'\b(?:token|memory) (?:budgets?|efficien\w*|compression|management)\b',
        r'\b(?:compact\w*|prun\w*|compress\w*)\b.{0,30}\b(?:context|tokens?|memory)\b',
        r'\b(?:long[ -]context|prompt caching|context caching)\b']),
    'measurement': ('Content Measurement & Attribution', '内容效果衡量与归因', [
        r'\b(?:content|marketing|click|product click) (?:attribution|analytics|outcomes?)\b',
        r'\bqualified (?:engagement|replies|buyer replies)\b', r'\bproduct clicks?\b']),
    'listening': ('Social Listening & Customer Signals', '社交聆听与客户信号', [
        r'\bsocial (?:listening|monitoring)\b', r'\bcustomer (?:signals?|insights?|conversations?)\b']),
    'security': ('Software Security & Evaluation', '软件安全与评估', [
        r'\b(?:security (?:flaws?|vulnerabilit\w*)|secure code|vulnerable software|cybersecurity)\b']),
}
GENERIC = {'agent','ai','workflow','system','model','tool','language','work','build','building','different','internal','logic','expected','true','ask','claude','coding'}


def concept_evidence(text):
    text = re.sub(r'https?://\S+|@[\w_]+', ' ', text.lower())
    return {key: sorted({m.group(0) for pattern in row[2] for m in re.finditer(pattern,text)})
            for key,row in CONCEPTS.items() if any(re.search(pattern,text) for pattern in row[2])}


WEAK_ORCHESTRATION={'multi-agent','multi agent','multiagent','multiple agents','multiple agent','agent teams','agent team'}


def shared_theme(a,b):
    # A generic coding/security connection must not collapse orchestration,
    # interoperability and oversight into a single "agents" mega-topic.
    shared=set(a) & set(b)
    if 'orchestration' in shared:
        strong_a=set(a['orchestration'])-WEAK_ORCHESTRATION
        strong_b=set(b['orchestration'])-WEAK_ORCHESTRATION
        # A shared broad multi-agent label cannot override different concrete
        # concerns (e.g. context compression versus human approval).
        if not (strong_a and strong_b) and (set(a)-{'orchestration'}) != (set(b)-{'orchestration'}):
            shared.remove('orchestration')
    return shared


def theme_for(evidence):
    profiles=[concept_evidence(p['text']) for p in evidence]
    counts=Counter(key for p in profiles for key in p)
    # Require majority support; ties use a stable editorial taxonomy order.
    eligible=[key for key in CONCEPTS if counts[key]>=max(1,len(evidence)//2+1)]
    eligible.sort(key=lambda key:(-counts[key],
        key=='orchestration' and all(not(set(p.get(key,[]))-WEAK_ORCHESTRATION) for p in profiles),
        list(CONCEPTS).index(key)))
    return (eligible[0] if eligible else None),profiles,counts

# Editorial experiments, not TelyClaw feature claims or factual source summaries.
EDITORIAL_MOVES = {
    'orchestration': 'Publish a handoff-ownership checklist; test recovery from a failed specialist before adding more agents.',
    'interoperability': 'Compare one task across two runtimes; document protocol compatibility, permissions and migration effort.',
    'coding': 'Show a coding-assistant review checklist; compare time saved against defects caught before approving a change.',
    'oversight': 'Map reversible versus consequential actions; propose approval checkpoints and measure intervention burden.',
    'context': 'Run one task with two context budgets; compare answer quality, retained evidence and token usage.',
    'measurement': 'Trace one editorial hypothesis to tagged clicks and qualified replies; separate reach from buyer intent.',
    'listening': 'Turn recurring customer questions into a content brief; validate relevance with independent sources and qualified replies.',
    'security': 'Create a reproducible security-review checklist; test failure cases before recommending deployment.',
}
