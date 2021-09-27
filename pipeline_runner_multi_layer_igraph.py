import re
from datetime import datetime
from typing import List

import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.process_tree import visualizer as pt_visualizer

from clustering_variant import ClusteringVariant
from distance_metrics import DistanceVariant
from label_splitter_multi_layer_igraph import LabelSplitter
from log_generator import LogGenerator
from performance_evaluator import PerformanceEvaluator
from post_processor import PostProcessor

evaluated_models = [('R_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt06-2056/logs/R_1_LogD_Sequence_mrt06-2056.xes.gz'),
                    ('AB_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt06-2056/logs/AB_1_LogD_Sequence_mrt06-2056.xes.gz'),
                    ('V_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_OD/feb17-1147/logs/V_1_LogD_Sequence_feb17-1147.xes.gz'),
                    ('J_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_OD/feb18-1515/logs/J_1_LogD_Sequence_feb18-1515.xes.gz'),
                    ('C_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt06-1652/logs/C_1_LogD_Sequence_mrt06-1652.xes')]


def run_pipeline_multi_layer_igraph(input_models=evaluated_models) -> None:
    for (name, path) in [('R_1',
                     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt06-2056/logs/R_1_LogD_Sequence_mrt06-2056.xes.gz')]:
        apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(name, [], path, 20000)


def apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(input_name: str,
                                                                         labels_to_split: List[str],
                                                                         log_path: str,
                                                                         max_number_of_traces: int):
    input_name = f'{input_name}_VARIANTS_ONLY'

    if not labels_to_split:
        print('Getting imprecise labels')
        complete_log = xes_importer.apply(log_path)
        labels_to_split = get_imprecise_labels(complete_log)
        print(labels_to_split)
    original_log = xes_importer.apply(log_path,
                                      parameters={
                                          xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: max_number_of_traces})
    write_data_from_original_log_with_imprecise_labels(input_name, original_log)

    if len(input_name) < 20:
        export_model_from_original_log_with_precise_labels(input_name, log_path)
    best_precision = 0

    for window_size in [3]:
        for distance in [DistanceVariant.EDIT_DISTANCE]:
            for threshold in [0]:
                log = xes_importer.apply(
                    log_path,
                    parameters={
                        xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: max_number_of_traces})

                best_precision = apply_pipeline_multi_layer_igraph_to_log(input_name,
                                                                             log,
                                                                             labels_to_split,
                                                                             original_log=original_log,
                                                                             threshold=threshold,
                                                                             window_size=window_size,
                                                                             number_of_traces=max_number_of_traces,
                                                                             distance_variant=distance,
                                                                             original_log_path=log_path,
                                                                             best_precision=best_precision)


def write_data_from_original_log_with_imprecise_labels(input_name, original_log):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        print(f'Starting pipeline for {input_name}')
        outfile.write('''



----------------------------------------------------------------------------------------------
Output from {date}
----------------------------------------------------------------------------------------------


                '''.format(date=datetime.now()))
        outfile.write('\nOriginal Data Performance:\n')

        original_net, initial_marking, final_marking = inductive_miner.apply(original_log)
        performance_evaluator = PerformanceEvaluator(original_net, initial_marking, final_marking, original_log,
                                                     outfile)
        performance_evaluator.evaluate_performance()
        original_tree = inductive_miner.apply_tree(original_log)
        pnml_exporter.apply(original_net, initial_marking,
                            f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_not_split_petri_net.pnml',
                            final_marking=final_marking)
        save_models_as_png(f'{input_name}_original_log_imprecise_labels', final_marking, initial_marking, original_net,
                           original_tree)


def export_model_from_original_log_with_precise_labels(input_name, path):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write('\n Data from log without imprecise labels\n')
        original_input_name = input_name.replace('_VARIANTS_ONLY', '')

        pattern = original_input_name + r'.*.xes.gz'
        log_path = re.sub(pattern, f'{original_input_name}_Log.xes.gz', path)

        print('log_path')
        print(log_path)

        original_log = xes_importer.apply(log_path)
        original_net, initial_marking, final_marking = inductive_miner.apply(original_log)
        performance_evaluator = PerformanceEvaluator(original_net, initial_marking, final_marking, original_log,
                                                     outfile)
        performance_evaluator.evaluate_performance()
        original_tree = inductive_miner.apply_tree(original_log)
        pnml_exporter.apply(original_net, initial_marking,
                            f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_not_split_petri_net.pnml',
                            final_marking=final_marking)
        save_models_as_png(f'{input_name}_original_log_precise_labels', final_marking, initial_marking, original_net,
                           original_tree)


def get_imprecise_labels(log: EventLog) -> list[str]:
    imprecise_labels = set()
    for trace in log:
        for event in trace:
            if event['OrgLabel'] != event['concept:name']:
                imprecise_labels.add(event['concept:name'])
    # print(imprecise_labels)
    return list(imprecise_labels)


def apply_pipeline_to_bpmn(input_type: str, threshold: float = 0.5,
                           window_size: int = 3):
    bpmn_graph = pm4py.read_bpmn(f'/home/jonas/repositories/pm-label-splitting/bpmn_files/{input_type}.bpmn')
    log_generator = LogGenerator()
    log = log_generator.get_log_from_bpmn(bpmn_graph)

    apply_pipeline_multi_layer_igraph_to_log(f'{input_type}', log, ['D'], log, threshold=threshold,
                                                window_size=window_size)


def apply_pipeline_multi_layer_igraph_to_log(input_type: str,
                                                log: EventLog,
                                                labels_to_split: list[str],
                                                original_log: EventLog,
                                                threshold: float = 0.5,
                                                window_size: int = 3,
                                                number_of_traces: int = 100000,
                                                distance_variant: DistanceVariant = DistanceVariant.EDIT_DISTANCE,
                                                clustering_variant: ClusteringVariant = ClusteringVariant.COMMUNITY_DETECTION,
                                                original_log_path: str = '',
                                                best_precision: float = 0,
                                                ) -> float:
    with open(f'./outputs/{input_type}.txt', 'a') as outfile:
        outfile.write('''

Parameters of this run:

Window size: {window_size}
Threshold for edges: {threshold}
Split candidates: {labels_to_split}
Max number of traces: {number_of_traces}
Method for distance calculation: {distance_variant}
Method for finding clusters: {clustering_variant}
Original log location: {original_log_path}

        '''.format(threshold=threshold,
                   window_size=window_size,
                   labels_to_split=''.join(labels_to_split),
                   number_of_traces=number_of_traces,
                   distance_variant=distance_variant,
                   clustering_variant=clustering_variant,
                   original_log_path=original_log_path))

        xes_exporter.apply(log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_used_log.xes')
        label_splitter = LabelSplitter(outfile,
                                       labels_to_split,
                                       threshold=threshold,
                                       window_size=window_size,
                                       distance_variant=distance_variant,
                                       clustering_variant=clustering_variant)
        split_log = label_splitter.split_labels(log)
        xes_exporter.apply(split_log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_split_log.xes')

        net, initial_marking, final_marking = inductive_miner.apply(split_log)
        tree = inductive_miner.apply_tree(split_log)

        post_processor = PostProcessor(label_splitter.get_split_labels_to_original_labels())
        final_net = post_processor.post_process_petri_net(net)

        outfile.write('\nPerformance split_log:\n')

        performance_evaluator = PerformanceEvaluator(final_net, initial_marking, final_marking, original_log, outfile)
        performance_evaluator.evaluate_performance()

        if performance_evaluator.precision > best_precision:
            print(f'Higher Precision found: {performance_evaluator.precision}')
            pnml_exporter.apply(final_net, initial_marking,
                                f'/home/jonas/repositories/pm-label-splitting/outputs/{input_type}_petri_net.pnml',
                                final_marking=final_marking)
            save_models_as_png(f'{input_type}_refined_process', final_marking, initial_marking, net, tree)
            return performance_evaluator.precision
        return best_precision


def save_models_as_png(name, final_marking, initial_marking, net, tree):
    gviz = pt_visualizer.apply(tree)
    pt_visualizer.save(gviz,
                       f'/mnt/c/Users/Jonas/Desktop/pm-label-splitting/result_pngs/{name}_tree.png')
    parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"}
    gviz_petri_net = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters)
    pn_visualizer.save(gviz_petri_net,
                       f'/mnt/c/Users/Jonas/Desktop/pm-label-splitting/result_pngs/{name}_net.png')