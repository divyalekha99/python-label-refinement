from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.conversion.bpmn import converter as bpmn_converter


class LogGenerator:
    # (First functionality: Generate log from petri net)
    # Input: BPMN Model
    # Output: Simulated event log
    # Optional parameters: Size of log, max case length
    # -> How does handling loops work?
    # Import BPMN Model
    # Convert to Petri Net (Reduce silent transitions??)
    # Play out Petri Net -> Generate simulated log

    def __init__(self):
        pass

    def get_log_from_bpmn(self, bpmn_graph: BPMN):
        net, im, fm = bpmn_converter.apply(bpmn_graph)
        event_log = simulator.apply(net, im, variant=simulator.Variants.BASIC_PLAYOUT,
                                    parameters={simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: 200})
        print(event_log)
        num_cases = len(event_log)
        print(num_cases)
        return event_log
