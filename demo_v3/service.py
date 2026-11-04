"""Read-only frozen CT4 audit plus independent experimental evidence rules.

CT4's old multiclass outputs cannot add, remove or veto evidence. Every raw
fragment is inferred for audit, including informational/emoji input; inference
faults propagate and never become undetermined/other_domain business labels.
"""
from pathlib import Path

from demo_v2.service import DemoService, ROOT
from demo_v3.detector import Detector, RULES_PATH
from demo_v3.ontology import aggregate


class Service:
    def __init__(self, root=ROOT, rules_path=RULES_PATH, frozen=None):
        self.ready = False
        self.status = {'rules':'invalid','sentiment':'invalid','topic':'invalid'}
        self.detector = None
        self.frozen = None
        try:
            self.detector = Detector(rules_path)
            self.status['rules'] = 'ready'
            self.frozen = frozen if frozen is not None else DemoService(Path(root))
            self.status.update(self.frozen.status)
            if self.frozen.ready is not True:
                raise ValueError('Frozen CT4/CT5 runtime or provenance invalid')
            self.ready = True
        except Exception:
            # Initialization errors are readiness faults; inference errors below
            # are deliberately not caught here or converted to business labels.
            self.ready = False

    def analyze(self, text):
        if not self.ready:
            raise RuntimeError('CT4 evidence service is not ready')
        evidence = self.detector.detect(text)
        clauses = []
        for clause in evidence.clauses:
            observed = self.frozen.predict(clause.text)
            clauses.append(dict(start=clause.start,end=clause.end,text=clause.text,
                                topics=sorted(clause.topics),positive=clause.positive,negative=clause.negative,
                                ct4=observed))
        output = dict(contract_version='3.0', **aggregate(evidence.positive,evidence.negative,evidence.topics))
        if len(evidence.topics) > 1:
            output['topics'] = [topic for topic in ('lecturer','curriculum','facility') if topic in evidence.topics]
        return output,dict(rules_version=self.detector.rules['version'],clauses=clauses,
                           ct4_role='audit_only_does_not_modify_evidence')

    def predict(self, text):
        return self.analyze(text)[0]
