"""Explicit migration of reusable ML algorithms, excluding old execution paths."""
import argparse
import ast
import re
from pathlib import Path

MAP={'ml.data':'feedback_ai.data.loader','ml.labels':'feedback_ai.common.labels','ml.preprocessing':'feedback_ai.data.preprocessing',
     'ml.train_sentiment':'feedback_ai.training.sentiment','ml.train_topic':'feedback_ai.training.topic',
     'ml.evaluate_sentiment':'feedback_ai.evaluation.sentiment','ml.evaluate_topic':'feedback_ai.evaluation.topic',
     'ml.predict_sentiment':'feedback_ai.inference.sentiment','ml.predict_topic':'feedback_ai.inference.topic'}

def migrate(source,target):
    def put(module,text):
        path=target/'src'/Path(*module.split('.')).with_suffix('.py');path.parent.mkdir(parents=True,exist_ok=True)
        for old,new in MAP.items():text=text.replace(old,new)
        path.write_text(text,encoding='utf-8')
    for old,new in MAP.items():
        if old in ('ml.labels','ml.preprocessing'):continue
        text=(source/Path(*old.split('.')).with_suffix('.py')).read_text(encoding='utf-8')
        # Keep importable algorithms; public CLI supplies all paths and guards outputs.
        tree=ast.parse(text);lines=text.splitlines(keepends=True)
        cut=next((n.lineno-1 for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='main'),len(lines))
        text=''.join(lines[:cut])
        put(new,text)
    selections={
        'ct2_class_weights':('class_weights','fit_candidate','select_candidate','_transitions','compare_results'),
        'ct3_word_char':('_pipeline','build_candidate','select_candidate','percentage_change','_percent_comparison'),
        'ct4_augmentation':('augment_train','collision_report','select_candidate','fit_candidate','_joint_transitions','comparison'),
        'ct5_selective_prediction':('partition_validation','fit_thresholds','apply_policy','_ratio','_metrics','_answerability','summarize')}
    names={'ct2_class_weights':'class_weights','ct3_word_char':'word_char','ct4_augmentation':'augmentation','ct5_selective_prediction':'selective'}
    prelude='''import hashlib
import math
import copy
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from feedback_ai.data.preprocessing import normalize_text
from feedback_ai.data.transforms import unaccent
from feedback_ai.common.labels import SENTIMENT_LABELS, TOPIC_LABELS
from feedback_ai.training.sentiment import TFIDF_PARAMS, CLF_PARAMS
from feedback_ai.evaluation.metrics import score_labels
LABELS={'sentiment':list(SENTIMENT_LABELS),'topic':list(TOPIC_LABELS)}
'''
    for old,functions in selections.items():
        text=(source/'reports'/f'{old}.py').read_text(encoding='utf-8');tree=ast.parse(text)
        allowed={'STRATEGIES','ORDER','TOL','CHAR_WEIGHTS','VARIANTS','RATIOS','QUANTILES','POLICIES'}
        nodes=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name in functions) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in allowed for t in n.targets))]
        extra=''
        if old=='ct3_word_char':extra='from feedback_ai.training.experiments.class_weights import class_weights, compare_results\n'
        if old=='ct4_augmentation':extra='from feedback_ai.training.experiments.class_weights import compare_results\nfrom feedback_ai.training.experiments.word_char import percentage_change\n'
        put('feedback_ai.training.experiments.'+names[old],prelude+extra+'\n\n'.join(ast.get_source_segment(text,n) for n in nodes)+'\n')
    text=(source/'reports/ct_evaluation.py').read_text(encoding='utf-8');tree=ast.parse(text)
    functions=['score_labels','score_cases']
    put('feedback_ai.evaluation.metrics','from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support\nfrom feedback_ai.common.labels import SENTIMENT_LABELS, TOPIC_LABELS\nLABELS={"sentiment":list(SENTIMENT_LABELS),"topic":list(TOPIC_LABELS)}\n'+'\n\n'.join(ast.get_source_segment(text,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in functions))
    for name in ('test_data','test_labels','test_preprocessing','test_sentiment_training','test_topic_training','test_demo_v3'):
        text=(source/'tests'/f'{name}.py').read_text(encoding='utf-8')
        for old,new in MAP.items():text=text.replace(old,new)
        text=text.replace("find_spec('demo_v3')","find_spec('feedback_ai')").replace('demo_v3.ontology','feedback_ai.inference.ontology').replace('demo_v3.detector','feedback_ai.inference.detector')
        # Existing real-data tests opt in; adapted fixture-only tests stay independent.
        path=target/'tests/unit'/f'{name}.py';path.write_text(text,encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--target',type=Path,required=True)
    a=p.parse_args();migrate(a.source.resolve(),a.target.resolve())
