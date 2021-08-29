# (Third functionality / step: Compute Performance)
# Input: Event Log
# Output: Performance results
# Mine model and check quality of the model
#
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet


class PerformanceEvaluator:
    def __init__(self):
        pass

    def get_precision(self, net: PetriNet, log: EventLog):
        pass

    def get_generalization(self, net: PetriNet, log: EventLog):
        pass

    def get_simplicity(self, net: PetriNet, log: EventLog):
        pass

    def get_fitness(self, net: PetriNet, log: EventLog):
        pass