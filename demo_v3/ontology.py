"""Business aggregation is independent of the experimental evidence detector."""
CORE_TOPICS = frozenset({'lecturer', 'curriculum', 'facility'})


def aggregate(positive: bool, negative: bool, topics) -> dict:
    if type(positive) is not bool or type(negative) is not bool:
        raise ValueError('Polarity evidence must be boolean')
    if isinstance(topics, (str, bytes)):
        raise ValueError('Topics must be a collection of core topic codes')
    unique = set(topics)
    if not unique <= CORE_TOPICS:
        raise ValueError('Unknown core topic')
    sentiment = {(True, True): 'mixed', (True, False): 'positive',
                 (False, True): 'negative', (False, False): 'undetermined'}[positive, negative]
    topic = 'other_domain' if not unique else next(iter(unique)) if len(unique) == 1 else 'education_quality'
    return dict(sentiment=sentiment, topic=topic)
