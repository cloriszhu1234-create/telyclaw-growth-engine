"""Local statistical NLP with inspectable evidence and deterministic score factors."""
import math
import re
from datetime import datetime
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_BRIEF = {'positioning': 'Provisional positioning: AI-assisted growth workflows with human judgment. Confirm TelyClaw product capabilities before publishing.',
                 'audience': 'B2B SaaS growth and marketing teams',
                 'keywords': ['ai', 'agents', 'growth', 'marketing', 'content', 'customer', 'social', 'engagement', 'attribution']}
WEIGHTS = {'relevance': .30, 'breadth': .20, 'engagement': .15, 'freshness': .15, 'momentum': .10, 'depth': .10}


def normalized(text):
    return re.sub(r'\W+', ' ', text.lower()).strip()


def detect(posts, prior, clock, hours, brief):
    # Reposts/identical copied text must not inflate independent evidence.
    unique = list({normalized(p['text']): p for p in reversed(posts)}.values())
    if not unique:
        return []
    prior = list({normalized(p['text']): p for p in reversed(prior)}.values())
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=3000)
    try:
        matrix = vectorizer.fit_transform([p['text'] for p in unique])
    except ValueError:
        return []
    labels = (AgglomerativeClustering(n_clusters=None, metric='cosine', linkage='average',
              distance_threshold=.78).fit_predict(matrix.toarray()) if len(unique) > 1 else [0])
    terms = vectorizer.get_feature_names_out()
    prior_matrix = vectorizer.transform([p['text'] for p in prior]) if prior else None
    topics = []
    for label in sorted(set(labels)):
        indexes = [i for i, x in enumerate(labels) if x == label]
        evidence = [unique[i] for i in indexes]
        centroid = np.asarray(matrix[indexes].mean(axis=0)).ravel()
        keywords = [terms[i] for i in centroid.argsort()[::-1] if centroid[i] > 0][:5]
        phrases = [k for k in keywords if ' ' in k]
        title = ' · '.join((phrases or keywords)[:2]).title()
        text = ' '.join(p['text'].lower() for p in evidence)
        matched = [k for k in brief['keywords'] if re.search(r'\b'+re.escape(k.lower())+r'\b', text)]
        relevance = min(100, len(matched)*25)
        authors = sorted({p['handle'] for p in evidence})
        engagement = sum(p['likes'] + 2*p['reposts'] + 2*p['replies'] for p in evidence)
        newest = min((clock-datetime.fromisoformat(p['created_at'])).total_seconds()/3600 for p in evidence)
        previous = 0
        if prior_matrix is not None:
            previous = int((cosine_similarity(prior_matrix, centroid.reshape(1, -1)).ravel() >= .22).sum())
        momentum = round((len(evidence)-previous)/previous*100) if previous else None
        factors = dict(relevance=relevance, breadth=min(100,len(authors)/5*100),
            engagement=min(100, math.log1p(engagement)/math.log1p(2000)*100),
            freshness=max(0,100*(1-newest/hours)),
            momentum=min(100,max(0,50+(momentum or 0)/4)) if previous else 50,
            depth=min(100,len(evidence)/5*100))
        factors = {k:round(v,1) for k,v in factors.items()}
        score = round(sum(WEIGHTS[k]*v for k,v in factors.items()),1)
        representative = max(indexes, key=lambda i:float(matrix[i].dot(centroid)[0]))
        topics.append(dict(id=str(label), title=title, keywords=keywords, summary=unique[representative]['text'],
            summary_method='Extractive: representative source text; not an independently verified claim.',
            factors=factors, weights=WEIGHTS, score=score, matched_keywords=matched, authors=authors,
            evidence=evidence, prior_count=previous, momentum=momentum, recommended=relevance>0,
            reason=f"{len(authors)} distinct accounts; {len(evidence)} unique posts; brand keyword matches: {', '.join(matched) or 'none'}. " +
                (f'{momentum:+}% unique-post change vs previous equal window.' if previous else 'No matching prior evidence; momentum unknown (neutral score).')))
    topics.sort(key=lambda t:(t['recommended'], t['score']), reverse=True)
    for i,t in enumerate(topics):
        t['rank'] = i+1
        t['top'] = i<3 and t['recommended']
    return topics
