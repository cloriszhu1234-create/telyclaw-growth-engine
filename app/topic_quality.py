"""Evidence-conditioned presentation only; does not change clusters or scores.

Rules refer to reusable technical concerns, never handles, products or post IDs.
All matches are retained for inspection; no LLM or external request is needed.
"""
import re
from .semantics import CONCEPTS, concept_evidence

FACETS = {
    'feedback': ('feedback and error recovery', '反馈与错误恢复',
                 r'\b(?:error feedback|feedback (?:loop|mechanism)|error (?:messages?|reporting|recovery)|debug\w*|troubleshoot\w*)\b'),
    'validation': ('testing and verification', '测试与验证',
                   r'\b(?:tests?|testing|verification|validation|verify|verified|evaluat\w*)\b'),
    'context': ('context and token efficiency', '上下文与 Token 效率',
                r'\b(?:context (?:compression|compaction|management|efficien\w*|budget\w*)|tokens? (?:efficien\w*|budget\w*|usage)|compress\w* (?:context|memory)|memory compression)\b'),
    'execution': ('execution harnesses and complex tasks', '执行框架与复杂任务',
                  r'\b(?:agent harness\w*|execution harness\w*|harness\w*|complex (?:software |engineering )?tasks?|software engineering tasks?)\b'),
}
LABELS = {
    'engineering': ('Engineering & Reliability of AI Coding Agents', 'AI 编程智能体的工程化与可靠性'),
    'feedback': ('Feedback & Error Recovery for AI Coding Agents', 'AI 编程智能体的反馈与错误恢复'),
    'validation': ('Testing & Verification for AI Coding Agents', 'AI 编程智能体的测试与验证'),
    'context': ('Context Efficiency for AI Coding Agents', 'AI 编程智能体的上下文效率'),
    'execution': ('Execution Harnesses for AI Coding Agents', 'AI 编程智能体的执行框架'),
    'protocols': ('AI Agent Interoperability & Communication Protocols', 'AI Agent 互操作性与通信协议'),
    'group_unknown': ('Provisional Discussion Cluster', '待确认的讨论主题'),
    'framework_choice': ('AI Agent Framework Selection', 'AI Agent 的框架选择'),
    'leadership_prompt': ('Prompt Templates for Engineering Leadership', '工程管理场景的提示词模板'),
    'prompt_template': ('Prompt Design & Templates', '提示词设计与模板'),
    'prompt_design': ('AI Prompt Design', 'AI 提示词设计'),
    'network_protocol': ('Network Protocols & Data Transport', '网络协议与数据传输'),
    'protocol_update': ('Protocol Updates', '协议更新'),
    'agent_discussion': ('AI Agent Discussion', 'AI Agent 相关讨论'),
}


def clean(text):
    # Attribution/links never establish the subject of a discussion.
    return re.sub(r'https?://\S+|@[\w_]+', ' ', text.lower())


def context_matches(text):
    """Match source phrases, not product names or claimed savings percentages.

    Bare tool output/compaction is ambiguous. Additional matches need both
    model/agent vocabulary and a context/prompt/memory connection. Keep this
    presentation rule separate from the clustering vocabulary and score inputs.
    """
    matches = {m.group(0) for m in re.finditer(FACETS['context'][2], text)}
    has_context = re.search(r'\b(?:context|prompt|working memory)\b', text)
    has_model = re.search(r'\b(?:agents?|assistants?|llms?|language models?|coding)\b', text)
    if has_context and has_model:
        matches.update(m.group(0) for m in re.finditer(r'\b(?:tool[ -]outputs?|compaction)\b', text))
    return sorted(matches)


def protocol_evidence(text):
    text = clean(text)
    if not re.search(r'\b(?:ai agents?|agents?|agentic|multi[ -]?agent)\b', text):
        return []
    return sorted({m.group(0) for m in re.finditer(
        r'\b(?:interoperabil\w*|communication protocols?|messaging protocols?|agent[ -]to[ -]agent|inter[ -]agent communication|agents? communicat\w*|agent protocols?)\b', text)})


def singleton_subject(post):
    """Describe a post's subject separately from its evidence strength.

    These are presentation rules, never clustering/relevance inputs. Each
    rule needs source phrases in the same local passage; handles, products
    and post IDs cannot select a title. Without a reliable domain label,
    use a visibly quoted excerpt rather than inventing a technical theme.
    """
    text = clean(post['text'])

    def nearby(*patterns):
        matches = [list(re.finditer(pattern, text)) for pattern in patterns]
        if not all(matches):
            return []
        for anchor in matches[0]:
            window = [anchor.group(0)]
            start, end = anchor.start(), anchor.end()
            for group in matches[1:]:
                near = [m for m in group if max(end, m.end()) - min(start, m.start()) <= 180]
                if not near:
                    break
                window.append(near[0].group(0))
                start, end = min(start, near[0].start()), max(end, near[0].end())
            else:
                return sorted(set(window))
        return []

    agent = r'\b(?:ai[ -]agents?|agents?|agentic)\b'
    prompt = r'\b(?:prompts?|prompting)\b'
    template = r'\b(?:templates?|system prompts?|instruction patterns?)\b'
    rules = [
        ('framework_choice', 'agent framework selection', '智能体框架选择',
         (agent, r'\bframeworks?\b')),
        ('leadership_prompt', 'prompt templates for engineering leadership', '工程管理提示词模板',
         (prompt, template, r'\b(?:engineering[ -](?:leads?|leaders?|leadership|managers?|management)|technical[ -](?:leads?|leadership)|tech leads?)\b')),
        ('prompt_template', 'prompt design and templates', '提示词设计与模板',
         (r'\b(?:prompt templates?|system prompts?|instruction templates?)\b',)),
        ('prompt_design', 'AI prompt design', 'AI 提示词设计',
         (prompt, r'\b(?:ai|llms?|language models?|chatbots?|coding agents?)\b')),
        ('network_protocol', 'network protocols and data transport', '网络协议与数据传输',
         (r'\bprotocols?\b', r'\bnetwork\w*\b', r'\b(?:transport|packets?|data transmission)\b')),
        ('protocol_update', 'protocol updates', '协议更新',
         (r'\bprotocols?\b', r'\bupdates?\b')),
        ('agent_discussion', 'AI agents', 'AI Agent', (r'\bai[ -]agents?\b',)),
    ]
    for key, en, zh, patterns in rules:
        matches = nearby(*patterns)
        if matches:
            return dict(zip(('en', 'zh'), LABELS[key])), [
                {'facet': 'subject', 'en': en, 'zh': zh,
                 'sources': [{'post_id': post['id'], 'handle': post['handle'], 'matches': matches}]}]

    # Clearly label this as a source-text subject, not a verified interpretation.
    original = re.sub(r'https?://\S+|@[\w_]+', ' ', post['text'])
    original = re.sub(r'\s+', ' ', original).strip()
    sentence = re.split(r'(?<=[.!?。！？])\s+', original)[0]
    excerpt = ' '.join(sentence.split()[:10])
    if len(excerpt) > 72:
        excerpt = excerpt[:72].rsplit(' ', 1)[0] or excerpt[:72]
    excerpt = excerpt.rstrip('.!?。！？ ')
    if len(excerpt) < len(sentence.rstrip('.!?。！？ ')):
        excerpt += '…'
    if not excerpt:
        return {'en': 'Source Text Needs Context', 'zh': '原帖信息不足，需补充上下文'}, []
    return {'en': f'Source topic: “{excerpt}”', 'zh': f'原帖议题：「{excerpt}」'}, []


def presentation(theme, evidence, fallback_title=None):
    total = len(evidence)
    profiles = [concept_evidence(p['text']) for p in evidence]
    concerns = []
    for key, (en, zh, pattern) in FACETS.items():
        rows = []
        for post, profile in zip(evidence, profiles):
            text = clean(post['text'])
            # A testing reference outside a coding context cannot rename a coding
            # cluster. This extra context affects presentation, never membership.
            coding = 'coding' in profile or (
                re.search(r'\bagents?\b', text) and re.search(r'\b(?:software engineering|coding|programming|code)\b', text))
            if theme == 'coding' and not coding:
                continue
            matches = context_matches(text) if key == 'context' else sorted({m.group(0) for m in re.finditer(pattern, text)})
            if matches:
                rows.append({'post_id': post['id'], 'handle': post['handle'], 'matches': matches})
        if rows:
            concerns.append({'facet': key, 'en': en, 'zh': zh, 'sources': rows})

    protocol_rows = [{'post_id': p['id'], 'handle': p['handle'], 'matches': protocol_evidence(p['text'])}
                     for p in evidence if protocol_evidence(p['text'])]
    labels = CONCEPTS[theme][:2] if theme else LABELS['group_unknown']
    supporting = {p['id'] for p, profile in zip(evidence, profiles) if theme and theme in profile}
    if theme == 'coding':
        facet_posts = {r['post_id'] for c in concerns for r in c['sources']}
        if total > 1 and len(concerns) >= 2 and len(facet_posts) >= total // 2 + 1:
            labels = LABELS['engineering']
        else:
            # A narrower name requires majority support for that concern.
            strong = [c for c in concerns if len(c['sources']) >= total // 2 + 1]
            if strong:
                key = strong[0]['facet']
                labels = LABELS[key]
    if len(protocol_rows) >= total // 2 + 1:
        labels = LABELS['protocols']
        supporting = {r['post_id'] for r in protocol_rows}
        concerns = [{'facet': 'protocols', 'en': 'interoperability and communication protocols',
                     'zh': '互操作性与通信协议', 'sources': protocol_rows}]

    names = dict(zip(('en', 'zh'), labels))
    singleton = total == 1 and not theme and not protocol_rows
    if singleton:
        names, concerns = singleton_subject(evidence[0])
    if not theme and total > 1 and not protocol_rows and fallback_title:
        clue = fallback_title.removesuffix(' Discussion')
        names = {'en': 'Provisional Discussion: ' + clue, 'zh': '待确认的讨论主题：' + clue}
    if singleton:
        clue = '; '.join(c['en'] for c in concerns)
        clue_zh = '、'.join(c['zh'] for c in concerns)
        insight = {
            'en': (f'Source wording supports the subject {clue}. ' if clue else
                   'The title quotes the source text; a more specific technical interpretation needs context. ') +
                  'This describes one post, not independent confirmation, verified benefit or accelerating discussion.',
            'zh': (f'原帖中的明确线索支持将议题描述为「{clue_zh}」。' if clue else
                   '标题摘取原帖内容；更具体的技术解释仍需结合上下文核实。') +
                  '这只是单条帖子的内容描述，不代表独立来源支持、已验证效果或讨论量加速。',
        }
    elif not theme and not protocol_rows:
        insight = {
            'en': 'The common technical issue is not reliably identified from the available text. Treat this signal as provisional and inspect the original sources before drawing conclusions.',
            'zh': '现有文本不足以可靠识别共同技术问题。请将其视为待确认信号，查看原始来源后再作判断。',
        }
    elif concerns:
        details = {}
        for language in ('en', 'zh'):
            details[language] = ('; ' if language == 'en' else '；').join(
                c[language] + ' (' + ', '.join('@' + h for h in sorted({r['handle'] for r in c['sources']})) + ')'
                for c in concerns)
        scope = len({r['post_id'] for c in concerns for r in c['sources']})
        insight = {
            'en': f"Evidence in {scope} of {total} selected posts connects this discussion through {details['en']}. This suggests an editorial question about {names['en'].lower()}, not evidence of consensus or accelerating discussion.",
            'zh': f"所选 {total} 条帖子中，{scope} 条提供了具体讨论线索：{details['zh']}。这些线索可用于提出关于「{names['zh']}」的内容议题，不代表行业共识或讨论量正在加速。",
        }
    else:
        insight = {
            'en': f"{len(supporting)} of {total} selected posts contain source vocabulary about {names['en'].lower()}. This identifies a discussion direction, not evidence of consensus or accelerating discussion.",
            'zh': f"所选 {total} 条帖子中，{len(supporting)} 条含有与「{names['zh']}」相关的明确语义线索。这只能识别讨论方向，不能证明行业共识或讨论量正在加速。",
        }
    return {'labels': names, 'insight': insight, 'support': concerns}
