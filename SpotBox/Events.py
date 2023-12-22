from collections import defaultdict

subscribers = defaultdict(list)


def subscribe(event_type, fn):
    subscribers[event_type].append(fn)


def post_event(event_type, data, data2=None):
    if event_type in subscribers:
        for fn in subscribers[event_type]:
            fn(event_type, data, data2)
