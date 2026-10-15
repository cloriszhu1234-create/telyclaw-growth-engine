"""Deterministic multi-document topic discovery; no external model or API needed."""
import hashlib
import math
import re
from datetime import datetime

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .semantics import CONCEPTS, GENERIC, concept_evidence, shared_theme, theme_for, EDITORIAL_MOVES

DEFAULT_BRIEF = {'positioning': 'Provisional positioning: AI-assisted growth workflows with human judgment. Confirm TelyClaw product capabilities before publishing.',
                 'audience': 'B2B SaaS growth and marketing teams',
                 'keywords': ['ai', 'agents', 'growth', 'marketing', 'content', 'customer', 'social', 'engagement', 'attribution']}
WEIGHTS = {'relevance': .30, 'momentum': .25, 'engagement': .15, 'breadth': .15, 'depth': .10, 'freshness': .05}
# General vocabulary equivalences, not topic names, post IDs or group assignments.
ALIASES = {
    'orchestrate':'orchestration', 'orchestrating':'orchestration', 'coordination':'orchestration',
    'coordinate':'orchestration', 'coordinating':'orchestration', 'coordinator':'orchestration',
    'multiagent':'multi agent', 'multi-agent':'multi agent', 'agentic':'agent',
    'llms':'language model', 'llm':'language model', 'chatbots':'chatbot',
    'programming':'coding', 'developer':'coding', 'developers':'coding', 'programmers':'coding',
    'software engineer':'coding engineer', 'software engineering':'coding engineering',
    'human-in-the-loop':'human approval', 'oversight':'approval', 'reviewer':'approval',
    'supervision':'approval', 'supervise':'approval', 'review':'approval',
    'monitoring':'listening', 'social media':'social', 'conversations':'conversation',
    'clients':'customer', 'customers':'customer', 'buyers':'buyer', 'audiences':'audience',
    'measurement':'attribution', 'measuring':'attribution', 'analytics':'attribution',
    'bookmarked':'bookmark', 'reposted':'repost', 'retweets':'repost',
    'cybersecurity':'security', 'vulnerabilities':'vulnerability', 'breaches':'breach',
}
EXTRA_STOP = {'ai','test','input','mock','data','https','http','www','com','post','posts','says','said','new','just','like','really','use','using','need','needs','team','teams','xxx','question','questions','discuss','discussing'}
STOP = set(ENGLISH_STOP_WORDS)|EXTRA_STOP


def normalized(text):
    return re.sub(r'\W+', ' ', text.lower()).strip()


def semantic_text(text,keep_stop=False):
    text = re.sub(r'https?://\S+|@[\w_]+', ' ', text.lower())
    for word, replacement in sorted(ALIASES.items(),key=lambda x:-len(x[0])):
        text = re.sub(r'\b'+re.escape(word)+r'\b',replacement,text)
    words = re.findall(r'[a-z][a-z0-9]*' if keep_stop else r'[a-z][a-z0-9]{2,}',text)
    # Light morphology retains readable concept words and requires no model download.
    words = [w[:-3]+'y' if w.endswith('ies') and w not in ('series','species') else w for w in words]
    words = [w[:-1] if w.endswith('s') and not w.endswith(('ss','ics','is')) else w for w in words]
    return ' '.join(words if keep_stop else (w for w in words if w not in STOP))


def compact(text,limit=180):
    text = re.sub(r'\s+',' ',text).strip()
    return text if len(text)<=limit else text[:limit].rsplit(' ',1)[0]+'…'


def feature_space(texts, raw_texts=None):
    vectorizer=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,max_features=5000)
    words=vectorizer.fit_transform(texts)
    characters=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),max_features=7000).fit_transform(texts)
    similarity=.8*cosine_similarity(words)+.2*cosine_similarity(characters)
    # Shared content concepts prevent a match based only on short character overlap.
    sets=[set(t.split())-GENERIC for t in texts]
    profiles=[concept_evidence(t) for t in (raw_texts or texts)]
    for i in range(len(texts)):
        for j in range(i):
            shared=shared_theme(profiles[i],profiles[j])
            if shared:
                similarity[i,j]=similarity[j,i]=max(similarity[i,j], .64)
            elif len(sets[i]&sets[j])<2 or (profiles[i] and profiles[j]):
                similarity[i,j]=similarity[j,i]=0
    np.fill_diagonal(similarity,1)
    return vectorizer,words,similarity


def topic_name(matrix,terms,texts,indexes):
    centroid=np.asarray(matrix[indexes].mean(axis=0)).ravel()
    counts=np.asarray((matrix[indexes]>0).sum(axis=0)).ravel()
    ranked=sorted(range(len(terms)),key=lambda i:centroid[i]*(1+math.log1p(counts[i])),reverse=True)
    keywords=[terms[i] for i in ranked if centroid[i]>0][:10]
    # Unknown domains retain a conservative content-word label, never a stitched
    # phrase whose original stop words changed the meaning.
    useful=[w for w in keywords if ' ' not in w and w not in GENERIC]
    return (useful[0].title()+' Discussion' if useful else 'Unclassified Discussion'),keywords,centroid


def detect(posts,prior,clock,hours,brief):
    unique=list({normalized(p['text']):p for p in reversed(posts)}.values())
    unique=[p for p in unique if semantic_text(p['text'])]
    if not unique:return []
    prior=list({normalized(p['text']):p for p in reversed(prior)}.values())
    texts=[semantic_text(p['text']) for p in unique]
    vectorizer,matrix,similarity=feature_space(texts,[p['text'] for p in unique])
    labels=(AgglomerativeClustering(n_clusters=None,metric='precomputed',linkage='average',distance_threshold=.69)
            .fit_predict(np.clip(1-similarity,0,1)) if len(unique)>1 else [0])
    terms=vectorizer.get_feature_names_out()
    prior_matrix=vectorizer.transform([semantic_text(p['text']) for p in prior]) if prior else None
    topics=[]
    for label in sorted(set(labels)):
        indexes=[i for i,x in enumerate(labels) if x==label]
        evidence=[unique[i] for i in indexes]
        title,keywords,centroid=topic_name(matrix,terms,[semantic_text(p['text'],keep_stop=True) for p in unique],indexes)
        theme,profiles,_=theme_for(evidence)
        if theme:title=CONCEPTS[theme][0]
        authors=sorted({p['handle'].lower().removeprefix('@') for p in evidence})
        # All documents contribute to features/title; summary includes attributed source excerpts.
        centrality=cosine_similarity(matrix[indexes],centroid.reshape(1,-1)).ravel()
        summary_sources=[p for _,p in sorted(zip(centrality,evidence),key=lambda item:-item[0])]
        excerpts=[{'handle':p['handle'],'excerpt':compact(re.split(r'(?<=[.!?])\s+',p['text'])[0],160)} for p in summary_sources]
        summary=(f"{len(evidence)} distinct posts from {len(authors)} accounts discuss {title.lower()}. " +
                 ' '.join(f"@{x['handle']}: “{x['excerpt']}”" for x in excerpts[:3]) +
                 (f" Plus {len(excerpts)-3} more supporting discussions below." if len(excerpts)>3 else ''))
        merged=' '.join(p['text'].lower()+' '+semantic_text(p['text']) for p in evidence)
        matched=[k for k in brief['keywords'] if re.search(r'\b'+re.escape(k.lower())+r'\b',merged)]
        # Relevance is an editorial heuristic. Generic AI/agent mentions alone
        # cannot establish audience fit. Specific configured terms and domain
        # themes provide explicit, inspectable evidence of a possible fit.
        generic={'ai','agent','agents','workflow','workflows'}
        specific=[k for k in matched if k.lower() not in generic]
        domain_fit=bool(theme and any(k.lower() in generic for k in brief['keywords']))
        relevance=min(100,len(specific)*25+(35 if domain_fit else 10 if matched else 0))
        measured=[p for p in evidence if any(p.get(k) is not None for k in ('likes','reposts','replies'))]
        available_engagement=sum(sum(p[k] for k in ('likes','reposts','replies') if p.get(k) is not None) for p in measured) if measured else None
        complete=all(all(p.get(k) is not None for k in ('likes','reposts','replies')) for p in evidence)
        engagement=(min(100,math.log1p(available_engagement/len(evidence))/math.log1p(2000)*100)*min(1,len(authors)/3) if complete else None)
        previous=[]
        if prior_matrix is not None:
            scores=cosine_similarity(prior_matrix,centroid.reshape(1,-1)).ravel()
            concepts=set(' '.join(texts[i] for i in indexes).split())
            previous=[p for p,score in zip(prior,scores) if
                      ((theme and theme in concept_evidence(p['text'])) or
                       (not theme and score>=.25 and len((concepts-GENERIC)&set(semantic_text(p['text']).split()))>=2))]
        def spread(rows):
            times=[datetime.fromisoformat(p['created_at']) for p in rows]
            return (max(times)-min(times)).total_seconds()/3600 if len(times)>1 else 0
        sufficient=(len(previous)>=3 and len(evidence)>=3 and len(authors)>=2 and
                    len({p['handle'].lower().removeprefix('@') for p in previous})>=2 and spread(previous)>=hours*.25 and spread(evidence)>=hours*.25)
        momentum=round((len(evidence)-len(previous))/len(previous)*100,1) if sufficient else None
        momentum_status=('Rising in observed sample' if momentum>0 else 'Flat / falling in observed sample') if sufficient else 'Insufficient historical data'
        newest=min((clock-datetime.fromisoformat(p['created_at'])).total_seconds()/3600 for p in evidence)
        factors=dict(relevance=relevance,momentum=max(0,min(100,momentum/2)) if momentum is not None else None,
            engagement=engagement,breadth=min(100,len(authors)/5*100),depth=min(100,35+len(authors)*10+min(20,len(set(key for profile in profiles for key in profile))*10)),freshness=max(0,min(100,100*(1-newest/hours))))
        factors={k:round(v,1) if v is not None else None for k,v in factors.items()}
        available=sum(WEIGHTS[k] for k,v in factors.items() if v is not None)
        weights={k:WEIGHTS[k]/available if factors[k] is not None else 0 for k in WEIGHTS}
        score=round(sum(weights[k]*v for k,v in factors.items() if v is not None),1)
        absence=[k for k,v in factors.items() if v is None]
        trending=(f"Observed: {len(evidence)} unique posts, {len(authors)} distinct accounts; " +
            (f'{available_engagement} available likes + reposts + replies' if available_engagement is not None else 'engagement not measured')+
            ('' if complete else ' (incomplete metrics; engagement scoring excluded)')+f'. {momentum_status}.'+
            (f' {momentum:+}% observed post-count change versus the previous equal window ({len(previous)} posts).' if momentum is not None else '')+
            (' Single-account signal, not independent confirmation.' if len(authors)==1 else '')+
            (' Missing factors excluded and remaining weights rescaled: '+', '.join(absence)+'.' if absence else ''))
        care=(f"Editorial hypothesis for {brief['audience']}: {title.lower()} connects through " +
            (', '.join(matched) if matched else ('configured AI editorial scope (domain heuristic; validate audience fit)' if domain_fit else 'no configured relevance keyword; review before prioritizing'))+
            f". Positioning supplied by you: {brief['positioning']} No additional product capabilities are assumed.")
        move=(f"Create a practical comparison about {title.lower()}: contrast “{excerpts[0]['excerpt']}”"+
            (f" with “{excerpts[1]['excerpt']}”" if len(excerpts)>1 else ' with a clearly labeled counter-hypothesis')+
            f". Give {brief['audience']} one decision checklist and one measurable experiment; do not repeat the source claims as established facts.")
        topics.append(dict(id=str(label),topic_key=hashlib.sha256(normalized(title).encode()).hexdigest()[:20],title=title,keywords=keywords,
            summary=summary,editorial_move=EDITORIAL_MOVES.get(theme,'Validate the source claim with a second independent account before committing to a content experiment.'),
            relevance_evidence={'specific_keywords':specific,'domain_fit':domain_fit,'theme':theme},
            theme=theme,theme_labels=({'en':CONCEPTS[theme][0],'zh':CONCEPTS[theme][1]} if theme else {}),
            concept_evidence=[{'post_id':p['id'],'concepts':profile} for p,profile in zip(evidence,profiles)],
            confirmation='multi_source' if len(authors)>1 else 'single_source',
            summary_method='Local multi-document extractive synthesis; attributed source excerpts are not independently verified.',
            discussion_points=excerpts, factors=factors,weights=weights,base_weights=WEIGHTS,score=score,matched_keywords=matched,
            metrics_complete=complete,available_engagement=available_engagement,engagement_coverage=f'{sum(all(p.get(k) is not None for k in ("likes","reposts","replies")) for p in evidence)}/{len(evidence)} posts have all three metrics',
            authors=authors,evidence=evidence,prior_count=len(previous),momentum=momentum,momentum_status=momentum_status,
            recommended=relevance>0,why_trending=trending,why_care=care,content_move=move,reason=trending,
            clustering_method='Local domain-concept vocabulary v1 + word/phrase TF-IDF (80%) + character similarity (20%); specific-concept similarity floor 0.64; average-link threshold 0.31. Generic agent/AI/workflow overlap alone is excluded. No remote model.'))
    topics.sort(key=lambda t:(t['recommended'],t['score']),reverse=True)
    for i,t in enumerate(topics):
        t['rank']=i+1;t['top']=i<3 and t['recommended']
    return topics
