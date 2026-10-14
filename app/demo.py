"""Fictional accounts, posts and engagement. Never actual X data."""
from datetime import datetime, timedelta, timezone

CLOCK = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
HANDLES = ['demo_ai_ops', 'demo_growthlab', 'demo_founder', 'demo_agentnews', 'demo_saasnotes', 'demo_builder']
DISCUSSIONS = [
    ('AI agents need human approval before publishing. Agent workflows should include human review, audit logs and clear ownership.',
     'Human approval makes AI agents useful for marketing. Agent workflows need review controls before publishing content.',
     'AI agent workflows fail when teams remove human approval. Review and ownership matter more than autonomous publishing.'),
    ('Social listening reveals customer questions before keyword reports. Social listening turns customer conversations into useful content.',
     'Customer questions are a better content brief than keyword volume. Social listening helps marketers find conversations with intent.',
     'Social listening needs context: recurring customer questions can reveal content opportunities before search demand appears.'),
    ('Content attribution should track qualified engagement and product clicks. Content measurement needs audience quality, not impressions alone.',
     'Qualified engagement beats raw impressions for B2B content attribution. Product clicks help connect content measurement to demand.',
     'Content attribution is hard when qualified engagement stays disconnected from product clicks. Track audience quality across content.'),
    ('Weekend football scores and stadium snacks. A great football match tonight.',
     'Football stadium tickets sold out after the match. Weekend football fans celebrate.',
     'Football match highlights from the stadium. Sports fans enjoyed the weekend.')
]


def posts():
    out = []
    for topic, texts in enumerate(DISCUSSIONS):
        for i, hours in enumerate([0.2, 0.45, 0.8, 1.7, 3, 5.5, 10, 19, 30, 65, 100, 160]):
            out.append(dict(id=f'demo:{topic}:{i}', handle=HANDLES[i % 6],
                text=texts[i % 3] + (' What should teams measure next?' if i % 2 else ''),
                created_at=(CLOCK-timedelta(hours=hours + topic*0.03)).isoformat(),
                likes=12 + (i*17+topic*9) % 160, reposts=3+i%11, replies=2+i%9,
                provenance='synthetic'))
    return out
