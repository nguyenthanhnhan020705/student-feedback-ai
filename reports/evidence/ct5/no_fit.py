"""Evidence launcher: CT5 run/replay with fitting APIs forbidden in this process."""
from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer


def forbidden(*args, **kwargs):
    raise AssertionError('CT5 milestone A must not fit or retrain')


Pipeline.fit = Pipeline.fit_transform = forbidden
FeatureUnion.fit = FeatureUnion.fit_transform = forbidden
LinearSVC.fit = forbidden
TfidfVectorizer.fit = TfidfVectorizer.fit_transform = forbidden
runpy.run_module('reports.ct5_selective_prediction', run_name='__main__')
