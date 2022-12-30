import copy
import csv
import os
import time
from typing import List, Tuple

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog

import clustering_method
from evaluation.apply_im import apply_im_without_noise_and_evaluate
from input_preprocessor import InputPreprocessor
from label_splitter.distance_metrics import Distance
from label_splitter.event_graphs_variant_based import get_event_graphs_from_event_log, EventGraphsVariantBased
from label_splitter.label_splitter_event_based import LabelSplitter as LabelSplitterEventBased
from label_splitter.label_splitter_variant_based import LabelSplitter as LabelSplitterVariantBased
from label_splitter.label_splitter_variant_multiplex import LabelSplitter as LabelSplitterVariantMultiplex
from pipeline.pipeline_helpers import export_models_and_pngs
from pipeline_helpers import get_tuples_for_folder, get_community_similarity, filter_duplicate_xor
from pipeline_variant import PipelineVariant
from utils.file_writer_helper import get_config_string, write_summary_file, \
    write_summary_file_with_parameters, run_start_string, setup_result_folder
from utils.input_data import InputData


def run_pipeline_for_artificial_event_logs(input_paths: List[Tuple[str, str]]) -> None:
    """
    Runs pipeline for set of artificial data
    :param input_paths: list of tuples of path and input prefix
    """
    for path, prefix in input_paths:
        input_list = get_tuples_for_folder(path, prefix)[::-1]
        apply_pipeline_to_folder(input_list, prefix, PipelineVariant.VARIANTS, labels_to_split=[], use_noise=False,
                                 use_frequency=True)


def run_pipeline_for_real_log(input_name: str, log_path: str, folder_name: str) -> None:
    """
    Runs the pipeline for a real log / individual log

    :param input_name: name to identify the log with
    :param log_path: path to the input event log
    :param folder_name: folder to associate with the log for the outputs
    """
    apply_pipeline_to_folder([(input_name, log_path)], folder_name,
                             PipelineVariant.VARIANTS,
                             labels_to_split=['9'],
                             use_frequency=True,
                             use_noise=False)


def apply_pipeline_to_folder(input_list: List[Tuple[str, str]], folder_name: str, pipeline_variant: PipelineVariant,
                             labels_to_split: List[str] = None, use_frequency: bool = True,
                             use_noise: bool = True) -> None:
    """
    Apply the whole pipeline to a folder of artificial event log.
    Sets up the output folder, input data for each log and applies the algorithm on the defined parameter space.
    """
    if labels_to_split is None:
        labels_to_split = []

    setup_result_folder(folder_name=folder_name, pipeline_variant=pipeline_variant)

    print("Starting pipeline")
    for (name, path) in input_list:
        input_data, input_preprocessor = set_up_input_data(folder_name, labels_to_split, name, path, pipeline_variant,
                                                           use_frequency, use_noise)

        if input_preprocessor.has_duplicate_xor():
            print('############## Skipped ######################')
            print('Duplicate XOR found, skipping model')
            with open(f'./outputs/best_results/{input_data.summary_file_name}', 'a') as outfile:
                outfile.write(
                    f'´\n----------------Skipped Model {input_data.input_name} because of duplicate label ------------------------\n')
            continue

        best_score, best_precision, best_configs = run_pipeline_on_parameter_space(input_data)
        try:
            write_summary_file_with_parameters(best_configs, best_score, best_precision, name,
                                               input_data.summary_file_name)
            write_summary_file(best_score, best_precision, input_data.ground_truth_precision, name,
                               input_data.summary_file_name,
                               input_data.xixi_precision, input_data.xixi_ari)
        except Exception as e:
            with open(f'./outputs/best_results/{input_data.summary_file_name}', 'a') as outfile:
                outfile.write(
                    f'´\n----------------Exception occurred while writing summary file------------------------\n')
                outfile.write(f'{repr(e)}\n')
            continue


def set_up_input_data(folder_name: str, labels_to_split: List[str], name: str, path: str,
                      pipeline_variant: PipelineVariant, use_frequency: bool, use_noise: bool) -> Tuple[
    InputData, InputPreprocessor]:
    """
    Generates the input data used throughout the pipeline for one event log.
    Calculates the original performance, unrefined performance, xixi performance and sets up naming

    :return: Preprocessed input data and input preprocessor
    """
    input_data = InputData(original_input_name=name,
                           log_path=path,
                           pipeline_variant=pipeline_variant,
                           labels_to_split=labels_to_split,
                           use_frequency=use_frequency,
                           use_noise=use_noise,
                           max_number_of_traces=5000000,
                           folder_name=folder_name)
    input_data.original_log = xes_importer.apply(input_data.log_path, parameters={
        xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: input_data.max_number_of_traces})
    input_data.input_name = f'{input_data.original_input_name}_{input_data.pipeline_variant}' if use_frequency else f'{input_data.original_input_name}_{input_data.pipeline_variant}'
    input_data.use_combined_context = False
    input_data.concurrent_labels = []
    summary_file_name = f'{folder_name}_{pipeline_variant}.txt' if use_frequency else f'{folder_name}_{pipeline_variant}.txt'
    input_data.summary_file_name = summary_file_name

    input_preprocessor = InputPreprocessor(input_data)
    input_preprocessor.preprocess_input()

    return input_data, input_preprocessor


def run_pipeline_on_parameter_space(input_data: InputData):
    """
    Runs the pipeline for one input data object on the whole parameter space.

    :return: Best results found and the configs used for the result
    """
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        print(f'Starting pipeline for {input_data.input_name}')
        outfile.write(run_start_string())

    best_precision = 0
    best_score = 0
    best_configs = []
    input_data.use_frequency = True

    event_graphs_variant_based = get_event_graphs_from_event_log(input_data.original_log, input_data.labels_to_split)

    for label in input_data.labels_to_split:
        for window_size in [1, 3, 5]:
            for distance in [Distance.EDIT_DISTANCE,
                             Distance.SET_DISTANCE,
                             Distance.MULTISET_DISTANCE]:
                for threshold in [0, 0.25, 0.5, 0.75, 1]:
                    try:
                        log = copy.deepcopy(input_data.original_log)

                        found_score, precision, f1_scores_refined = apply_pipeline_to_log(input_data, log, distance,
                                                                                          window_size, threshold,
                                                                                          best_score,
                                                                                          event_graphs_variant_based)

                        config_string = get_config_string(clustering_method.ClusteringMethod.COMMUNITY_DETECTION,
                                                          distance,
                                                          input_data.labels_to_split, input_data.max_number_of_traces,
                                                          input_data.log_path, threshold, window_size,
                                                          use_frequency=input_data.use_frequency)
                        if found_score > best_score:
                            best_configs = [config_string]
                            best_score = found_score
                            best_precision = precision
                        elif round(found_score, 2) == round(best_score, 2):
                            best_configs.append(config_string)
                    except Exception as e:
                        print('----------------Exception occurred while running pipeline ------------------------')
                        print(repr(e))

                        with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
                            outfile.write(f'´\n----------------Exception occurred------------------------\n')
                            outfile.write(f'{window_size}\n')
                            outfile.write(f'{threshold}\n')
                            outfile.write(f'{distance}\n')
                            outfile.write(f'{input_data.use_combined_context}\n')
                        continue

    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write('Best precision found:\n')
        outfile.write(str(best_precision))
    return best_score, best_precision, best_configs


def apply_pipeline_to_log(input_data: InputData,
                          log: EventLog,
                          distance_variant: Distance,
                          window_size: int,
                          threshold: float,
                          best_score: float,
                          event_graphs_variant_based: EventGraphsVariantBased):
    """
    Applies the algorithm with the specified to the input event log

    :return: ARI, precision and F1-scores of the model generated from the refined event log
    """
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write(get_config_string(clustering_method.ClusteringMethod.COMMUNITY_DETECTION, distance_variant,
                                        input_data.labels_to_split, input_data.max_number_of_traces,
                                        input_data.log_path, threshold, window_size, input_data.use_frequency))
        start = time.time()
        # Apply the label splitting algorithm
        label_splitter = get_label_splitter(distance_variant, input_data, outfile,
                                            threshold, window_size, event_graphs_variant_based)

        split_log = label_splitter.split_labels(log)
        split_log_clustering = filter_duplicate_xor(split_log, input_data.labels_to_split,
                                                    label_splitter.found_clustering)
        end = time.time()
        runtime = end - start
        outfile.write(f'\nRuntime: {runtime}\n')
        outfile.write('\nPerformance split_log:\n')
        outfile.write('\nIM without threshold:\n')
        labels_to_original = label_splitter.get_split_labels_to_original_labels()

        # Export the split log
        xes_exporter.apply(split_log,
                           f'./outputs/{input_data.input_name}_{threshold}_{window_size}_{distance_variant}.xes.gz')

        calculate_unrefined_log_precision(input_data, label_splitter, labels_to_original, outfile)

        # Generate a model from the split data and evaluate it.
        final_marking, initial_marking, final_net, precision, simplicity, generalization, fitness = apply_im_without_noise_and_evaluate(
            labels_to_original,
            split_log,
            input_data.original_log,
            outfile,
            label_splitter.short_label_to_original_label)

        f1_scores_refined = []
        if input_data.ground_truth_clustering:
            ari_score = get_community_similarity(input_data.ground_truth_clustering, split_log_clustering)
        else:
            ari_score = precision
        outfile.write(f'\nAdjusted Rand Index:\n')
        outfile.write(f'{ari_score}\n\n')

        write_results_to_csv(ari_score, distance_variant, fitness, generalization, input_data, label_splitter,
                             precision, runtime, simplicity, threshold, window_size)

        if ari_score > best_score:
            # Export everything is new best model was found
            print(f'\nHigher Adjusted Rand Index found: {ari_score}')
            print(f'\nPrecision of found clustering: {precision}')
            tree = inductive_miner.apply_tree(split_log)
            export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_data.input_name,
                                   f'{input_data.input_name}_{threshold}_{distance_variant}_{window_size}_split_log')

        return ari_score, precision, f1_scores_refined


def calculate_unrefined_log_precision(input_data, label_splitter, labels_to_original, outfile):
    if input_data.original_log_precision == 0:
        print('Starting to get original performance')
        final_marking, initial_marking, final_net, original_precision, original_simplicity, original_generalization, original_fitness = apply_im_without_noise_and_evaluate(
            labels_to_original,
            input_data.original_log,
            input_data.original_log,
            outfile,
            label_splitter.short_label_to_original_label)
        input_data.original_log_precision = original_precision
        input_data.original_log_simplicity = original_simplicity
        input_data.original_log_generalization = original_generalization
        input_data.original_log_fitness = original_fitness
        print('finished original log calculation')


def write_results_to_csv(ari_score: float, distance_variant: Distance, fitness: float, generalization: float,
                         input_data: InputData, label_splitter: LabelSplitterVariantBased, precision: float,
                         runtime: float, simplicity: float, threshold: float, window_size: int) -> None:
    with open(f'./results/{input_data.folder_name}_{input_data.pipeline_variant}_NEW.csv', 'a') as f:
        writer = csv.writer(f)
        if input_data.ground_truth_clustering:
            row = [input_data.original_input_name, input_data.max_number_of_traces,
                   ' '.join(input_data.labels_to_split),
                   ', '.join(input_data.original_labels), input_data.original_log_precision,
                   input_data.original_log_simplicity, input_data.original_log_generalization,
                   input_data.original_log_fitness,
                   len(input_data.xixi_clustering),
                   input_data.xixi_precision, input_data.xixi_ari,
                   input_data.use_combined_context, input_data.use_frequency, window_size, distance_variant, threshold,
                   len(label_splitter.found_clustering), precision, ari_score, simplicity, generalization, fitness,
                   runtime]
        else:
            row = [input_data.original_input_name, input_data.max_number_of_traces,
                   ' '.join(input_data.labels_to_split),
                   '[]', input_data.original_log_precision,
                   input_data.original_log_simplicity, input_data.original_log_generalization,
                   input_data.original_log_fitness,
                   0, 0, 0,
                   input_data.use_combined_context, input_data.use_frequency, window_size, distance_variant, threshold,
                   len(label_splitter.found_clustering), precision, ari_score, simplicity, generalization,
                   fitness, runtime]
        writer.writerow(row)


def get_label_splitter(distance_variant: Distance, input_data: InputData, outfile, threshold, window_size,
                       event_graphs_variant_based: EventGraphsVariantBased):
    if input_data.pipeline_variant == PipelineVariant.VARIANTS:
        label_splitter = LabelSplitterVariantBased(outfile,
                                                   input_data.labels_to_split,
                                                   threshold=threshold,
                                                   window_size=window_size,
                                                   distance_variant=distance_variant,
                                                   clustering_variant=clustering_method.ClusteringMethod.COMMUNITY_DETECTION,
                                                   use_frequency=input_data.use_frequency,
                                                   concurrent_labels=input_data.concurrent_labels,
                                                   use_combined_context=input_data.use_combined_context,
                                                   event_graphs_variant_based=event_graphs_variant_based)
    elif input_data.pipeline_variant == PipelineVariant.VARIANTS_MULTIPLEX:
        label_splitter = LabelSplitterVariantMultiplex(outfile,
                                                       input_data.labels_to_split,
                                                       threshold=threshold,
                                                       window_size=window_size,
                                                       distance_variant=distance_variant,
                                                       clustering_variant=clustering_method.ClusteringMethod.COMMUNITY_DETECTION,
                                                       use_frequency=input_data.use_frequency,
                                                       use_combined_context=input_data.use_combined_context)
    else:
        label_splitter = LabelSplitterEventBased(outfile,
                                                 input_data.labels_to_split,
                                                 threshold=threshold,
                                                 window_size=window_size,
                                                 distance_variant=distance_variant,
                                                 clustering_variant=clustering_method.ClusteringMethod.COMMUNITY_DETECTION,
                                                 use_combined_context=input_data.use_combined_context)
    return label_splitter
