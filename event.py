from pm4py.objects.log.obj import Event

# Representation of an event with advanced properties (prefix, suffix)
# Allow for different types of suffix (sequence, multi-set, set)
class TestEvent(Event):
    def __init__(self, event: Event):
        pass