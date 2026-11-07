"""Specification tests, not an independent semantic evaluation set."""
import importlib.util
import itertools
import unicodedata

import pytest


def modules():
    assert importlib.util.find_spec('feedback_ai') is not None, 'v3 evidence engine is missing'
    from feedback_ai.inference.ontology import aggregate
    from feedback_ai.inference.detector import Detector
    return aggregate, Detector


@pytest.mark.parametrize('positive,negative', itertools.product([False, True], repeat=2))
@pytest.mark.parametrize('bits', itertools.product([False, True], repeat=3))
def test_aggregation_exhausts_boolean_and_core_topic_sets(positive, negative, bits):
    aggregate, _ = modules()
    topics = [t for t, enabled in zip(('lecturer','curriculum','facility'), bits) if enabled]
    expected_sentiment = {(False,False):'undetermined',(True,False):'positive',
                          (False,True):'negative',(True,True):'mixed'}[positive,negative]
    expected_topic = 'other_domain' if not topics else topics[0] if len(topics)==1 else 'education_quality'
    assert aggregate(positive,negative,topics+topics) == dict(sentiment=expected_sentiment,topic=expected_topic)


@pytest.mark.parametrize('args', [(1,False,[]),(False,None,[]),(False,False,['other']),
                                  (False,False,'lecturer'),(False,False,[[]])])
def test_aggregation_rejects_invalid_evidence(args):
    aggregate, _ = modules()
    with pytest.raises((ValueError,TypeError)):
        aggregate(*args)


SPEC = [
 ('Thầy giảng bài rõ ràng và phòng học thì nóng.','mixed','education_quality'),
 ('Giảng viên nhiệt tình và phòng học sạch đẹp.','positive','education_quality'),
 ('Cô dạy rất hay nhưng đôi lúc giải thích khó hiểu.','mixed','lecturer'),
 ('Giảng viên thiếu nhiệt tình và phòng thực hành có nhiều máy hỏng.','negative','education_quality'),
 ('Giảng viên nhiệt tình, nội dung môn học thiết thực và phòng học sạch sẽ.','positive','education_quality'),
 ('Thầy và cô đều giảng bài dễ hiểu.','positive','lecturer'),
 ('Chương trình có quá nhiều lý thuyết và thiếu giờ thực hành.','negative','curriculum'),
 ('Máy tính trong phòng thực hành thường xuyên bị hỏng.','negative','facility'),
 ('Môn học có ba tín chỉ.','undetermined','curriculum'),
 ('Giảng viên sử dụng slide trong các buổi học.','undetermined','lecturer'),
 ('Phòng học có máy chiếu.','undetermined','facility'),
 ('Giảng viên thông báo lịch học và phòng học ở tầng hai.','undetermined','education_quality'),
 ('Tốt.','positive','other_domain'),
 ('Thay giang bai de hieu va rat nhiet tinh.','positive','lecturer'),
 ('🙂🙂🙂','undetermined','other_domain'),
]


@pytest.mark.parametrize('text,sentiment,topic', SPEC)
@pytest.mark.parametrize('form', ['NFC','NFD'])
def test_detector_binding_examples(text,sentiment,topic,form):
    aggregate, Detector = modules()
    evidence = Detector().detect(unicodedata.normalize(form,text))
    assert aggregate(evidence.positive,evidence.negative,evidence.topics) == dict(sentiment=sentiment,topic=topic)
    assert evidence.clauses and all(text[clause.start:clause.end] or form=='NFD' for clause in evidence.clauses)


@pytest.mark.parametrize('text,sentiment,topic', [
 ('Thầy không nhiệt tình.','negative','lecturer'),
 ('Bài giảng không khó hiểu như em nghĩ.','positive','lecturer'),
 ('Cô dạy tốt, không hề khó hiểu.','positive','lecturer'),
 ('Từ "tốt" và "tệ" là hai ví dụ.','undetermined','other_domain'),
 ('Cụm từ giảng viên và phòng học xuất hiện trên trang.','undetermined','other_domain'),
 ('"Giảng viên rất tốt" là một câu ví dụ.','undetermined','other_domain'),
 ('Không bàn về phòng học; thầy giảng dễ hiểu.','positive','lecturer'),
 ('Thầy dạy tốt. Quán phở rất ngon.','positive','lecturer'),
 ('Thầy dạy tốt; cô giải thích khó hiểu.','mixed','lecturer'),
 ('Giảng viên nói từ "khó hiểu" trong bài.','undetermined','lecturer'),
])
def test_detector_context_prevents_false_mixed_and_topics(text,sentiment,topic):
    aggregate, Detector = modules()
    evidence = Detector().detect(text)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics) == dict(sentiment=sentiment,topic=topic)


def test_evidence_offsets_preserve_raw_text_and_attach_subjects():
    _, Detector = modules()
    raw = 'Thầy giảng dễ hiểu; phòng học nóng.'
    evidence = Detector().detect(raw)
    assert [raw[c.start:c.end] for c in evidence.clauses] == ['Thầy giảng dễ hiểu',' phòng học nóng']
    assert evidence.clauses[0].topics == frozenset({'lecturer'})
    assert evidence.clauses[1].topics == frozenset({'facility'})
    assert evidence.clauses[0].positive and evidence.clauses[1].negative


def test_quoted_punctuation_cannot_unmask_predicates():
    aggregate, Detector = modules()
    result = Detector().detect('"Thầy dạy tốt; phòng học nóng" là câu ví dụ.')
    assert aggregate(result.positive,result.negative,result.topics) == dict(sentiment='undetermined',topic='other_domain')


def test_va_splits_asserted_subjects_but_not_coordinated_lecturers():
    _, Detector = modules()
    evidence = Detector().detect('Thầy giảng rõ ràng và phòng học nóng.')
    assert len(evidence.clauses)==2
    assert [c.topics for c in evidence.clauses] == [frozenset({'lecturer'}),frozenset({'facility'})]
    assert len(Detector().detect('Thầy và cô đều giảng dễ hiểu.').clauses)==1


@pytest.mark.parametrize('text,topic',[
    ('Giảng viên yêu cầu tìm từ tốt và tệ.','lecturer'),
    ('Phòng học mang tên Tốt.','facility'),
    ('Giảng viên viết cụm từ phòng học nóng trên bảng.','lecturer'),
])
def test_unquoted_vocabulary_mentions_are_not_asserted_predicates(text,topic):
    aggregate,Detector=modules()
    evidence=Detector().detect(text)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)==dict(sentiment='undetermined',topic=topic)


@pytest.mark.parametrize('text,topic',[
    ('Phòng học có rất nhiều máy chiếu.','facility'),
    ('Cô sử dụng slide trong lớp.','lecturer'),
    ('Phòng học có nhiệt độ nóng.','facility'),
])
@pytest.mark.parametrize('form',['NFC','NFD'])
def test_accented_have_and_teacher_remain_distinct(text,topic,form):
    aggregate,Detector=modules()
    evidence=Detector().detect(unicodedata.normalize(form,text))
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)['topic']==topic


@pytest.mark.parametrize('text',[
    'Giảng viên thông báo cho bạn.',
    'Phòng học có bàn ghế.',
    'Giảng viên nhắc các bạn và thấy lịch học.',
])
def test_accented_pronouns_and_furniture_are_information_only(text):
    aggregate,Detector=modules()
    evidence=Detector().detect(text)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)['sentiment']=='undetermined'


@pytest.mark.parametrize('quotes', [('"','"'),("'","'"),('“','”'),('‘','’')],
                         ids=['straight-double','straight-single','curly-double','curly-single'])
@pytest.mark.parametrize('form',['NFC','NFD'])
def test_review_r1_multiline_paired_quotes_never_create_evidence(quotes,form):
    aggregate,Detector=modules()
    left,right=quotes
    raw=unicodedata.normalize(form,left+'Giảng viên tốt\nphòng học nóng'+right+' là câu ví dụ.')
    detector=Detector()
    masked=detector._mask_quotes(raw)
    assert len(masked)==len(raw)
    close=raw.rfind(right)
    assert not masked[:close+len(right)].strip()
    assert masked[close+len(right):]==raw[close+len(right):]
    evidence=detector.detect(raw)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)==dict(sentiment='undetermined',topic='other_domain')
    assert all(raw[c.start:c.end]==c.text for c in evidence.clauses)


@pytest.mark.parametrize('text,sentiment,topic',[
    ('Giảng viên viết cụm từ tốt và phòng học nóng trên bảng.','undetermined','lecturer'),
    ('Cụm từ tốt nhưng tệ xuất hiện trên trang.','undetermined','other_domain'),
    ('Giảng viên viết cụm từ tốt và phòng học nóng trên bảng; chương trình thiết thực.','positive','education_quality'),
    ('Cụm từ tốt nhưng tệ xuất hiện trên trang. Giảng viên nhiệt tình.','positive','lecturer'),
    ('Giảng viên viết cụm từ tốt và tệ trên bảng nhưng phòng học nóng.','negative','education_quality'),
    ('Cụm từ tốt nhưng tệ xuất hiện trên trang và giảng viên nhiệt tình.','positive','lecturer'),
])
@pytest.mark.parametrize('form',['NFC','NFD'])
def test_review_r2_mentions_keep_scope_and_release_later_assertions(text,sentiment,topic,form):
    aggregate,Detector=modules()
    raw=unicodedata.normalize(form,text)
    evidence=Detector().detect(raw)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)==dict(sentiment=sentiment,topic=topic)
    assert all(raw[c.start:c.end]==c.text for c in evidence.clauses)


@pytest.mark.parametrize('text,sentiment,topic',[
    ('Giảng viên từ trường khác đến và dạy tốt.','positive','lecturer'),
    ('Giảng viên nhiệt tình và từ phòng học phát ra tiếng ồn.','positive','education_quality'),
    ('Từ phòng học, giảng viên thông báo lịch học.','undetermined','education_quality'),
])
@pytest.mark.parametrize('form',['NFC','NFD'])
def test_review_r3_source_preposition_preserves_following_evidence(text,sentiment,topic,form):
    aggregate,Detector=modules()
    evidence=Detector().detect(unicodedata.normalize(form,text))
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)==dict(sentiment=sentiment,topic=topic)


@pytest.mark.parametrize('text,sentiment,topic',[
    ('Từ tốt và tệ xuất hiện trên trang.','undetermined','other_domain'),
    ('Từ tốt xuất hiện trên bảng.','undetermined','other_domain'),
    ('Từ tốt xuất hiện trên bảng nhưng phòng học nóng.','negative','facility'),
    ('Giảng viên từ trường khác đến và dạy tốt.','positive','lecturer'),
    ('Giảng viên nhiệt tình và từ phòng học phát ra tiếng ồn.','positive','education_quality'),
])
@pytest.mark.parametrize('form',['NFC','NFD'])
def test_review_r4_word_occurrence_and_source_prepositions(text,sentiment,topic,form):
    aggregate,Detector=modules()
    raw=unicodedata.normalize(form,text)
    evidence=Detector().detect(raw)
    assert aggregate(evidence.positive,evidence.negative,evidence.topics)==dict(sentiment=sentiment,topic=topic)
    assert all(raw[c.start:c.end]==c.text for c in evidence.clauses)
