import random

import editdistance
import pandas as pd
import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.obj import EventLog
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.process_tree import converter
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer

from label_splitter import LabelSplitter
from log_generator import LogGenerator
from performance_evaluator import PerformanceEvaluator
from post_processor import PostProcessor


def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')
    num_events = len(event_log)
    num_cases = len(event_log.case_id.unique())
    print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))


def main() -> None:
    apply_pipeline_to_bpmn('loop_example', threshold=0.75,
                           window_size=3)  # threshold=0 also works, 0.5 produces wrong results
    c_1_log = xes_importer.apply(
        '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt06-1652/logs/C_1_LogD_Sequence_mrt06-1652.xes')

    apply_pipeline('c_1', c_1_log, get_imprecise_labels(c_1_log), threshold=0.5, window_size=3)


def get_imprecise_labels(log: EventLog) -> list[str]:
    imprecise_labels = set()
    for trace in log:
        for event in trace:
            if event['OrgLabel'] != event['concept:name']:
                imprecise_labels.add(event['concept:name'])
    print(imprecise_labels)
    return list(imprecise_labels)


def apply_pipeline_to_bpmn(input_type: str, threshold: float = 0.5,
                           window_size: int = 3):
    bpmn_graph = pm4py.read_bpmn(f'/home/jonas/repositories/pm-label-splitting/bpmn_files/{input_type}.bpmn')
    log_generator = LogGenerator()
    log = log_generator.get_log_from_bpmn(bpmn_graph)

    apply_pipeline(f'{input_type}', log, ['D'], threshold=threshold, window_size=window_size)


def apply_pipeline(input_type: str, log: EventLog, labels_to_split: list[str], threshold: float = 0.5,
                   window_size: int = 3):
    xes_exporter.apply(log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_original_log.xes')
    label_splitter = LabelSplitter(labels_to_split, threshold=threshold, window_size=window_size)
    split_log = label_splitter.split_labels(log)
    xes_exporter.apply(split_log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_split_log.xes')
    net, initial_marking, final_marking = inductive_miner.apply(split_log)
    post_processor = PostProcessor(label_splitter.get_split_labels_to_original_labels())
    final_net = post_processor.post_process_petri_net(net)
    pnml_exporter.apply(final_net, initial_marking,
                        f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_petri_net.pnml',
                        final_marking=final_marking)
    print('split_log:')
    original_log = xes_importer.apply(
        f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_original_log.xes')
    performance_evaluator = PerformanceEvaluator(final_net, initial_marking, final_marking, original_log)
    performance_evaluator.evaluate_performance()
    print('original_log:')
    original_net, initial_marking, final_marking = inductive_miner.apply(original_log)
    performance_evaluator = PerformanceEvaluator(original_net, initial_marking, final_marking, original_log)
    performance_evaluator.evaluate_performance()
    pnml_exporter.apply(original_net, initial_marking,
                        f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_original_petri_net.pnml',
                        final_marking=final_marking)
    # export_bpmn_model(log)


def export_bpmn_model(log):
    tree = pm4py.discover_process_tree_inductive(log)
    bpmn_graph = converter.apply(tree, variant=converter.Variants.TO_BPMN)
    pm4py.write_bpmn(bpmn_graph, '/home/jonas/repositories/pm-label-splitting/test_files/test.bpmn', enable_layout=True)
    # gviz = pt_visualizer.apply(tree)
    # pt_visualizer.view(gviz)


main()
