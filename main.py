import editdistance
import pandas as pd
import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.process_tree import converter


from label_splitter import LabelSplitter
from log_generator import LogGenerator


def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')
    num_events = len(event_log)
    num_cases = len(event_log.case_id.unique())
    print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))


def main() -> None:
    import_csv('/mnt/c/Users/Jonas/Downloads/running-example.csv')
    bpmn_graph = pm4py.read_bpmn('/mnt/c/Users/Jonas/Downloads/diagram.bpmn')

    log_generator = LogGenerator()
    log = log_generator.get_log_from_bpmn(bpmn_graph)

    label_splitter = LabelSplitter()
    split_log = label_splitter.split_labels(log)
    xes_exporter.apply(split_log, '/home/jonas/repositories/pm-label-splitting/test_files/test.xes')

    net, initial_marking, final_marking = inductive_miner.apply(split_log)
    print(net)
    tree = pm4py.discover_process_tree_inductive(log)

    bpmn_graph = converter.apply(tree, variant=converter.Variants.TO_BPMN)
    pm4py.write_bpmn(bpmn_graph, '/home/jonas/repositories/pm-label-splitting/test_files/test.bpmn', enable_layout=True)

    # gviz = pt_visualizer.apply(tree)
    # pt_visualizer.view(gviz)



main()
