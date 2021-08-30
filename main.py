import editdistance
import pandas as pd
import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
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
    apply_pipeline('loop_example', ['D'])


def apply_pipeline(input_type: str, labels_to_split: list[str]):
    bpmn_graph = pm4py.read_bpmn(f'/home/jonas/repositories/pm-label-splitting/bpmn_files/{input_type}.bpmn')
    log_generator = LogGenerator()
    log = log_generator.get_log_from_bpmn(bpmn_graph)
    xes_exporter.apply(log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_original_log.xes')

    label_splitter = LabelSplitter(labels_to_split)
    split_log = label_splitter.split_labels(log)
    xes_exporter.apply(split_log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_split_log.xes')
    net, initial_marking, final_marking = inductive_miner.apply(split_log)
    post_processor = PostProcessor()
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
