from feedback_ai.common.display import TOPICS
def aspects(clauses):
    found = {t for c in clauses for t in c['topics']}
    result = {}
    for topic in TOPICS:
        if topic not in found: continue
        certain = [c for c in clauses if c['topics']==[topic]]
        positive = any(c['positive'] for c in certain)
        negative = any(c['negative'] for c in certain)
        result[topic] = {(True,True):'mixed',(True,False):'positive',(False,True):'negative',(False,False):'undetermined'}[positive,negative]
    return result
