import re
from typing import List

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog

import clustering_variant
from apply_im import apply_im_with_noise_and_export, apply_im_without_noise_and_export, \
    write_data_from_original_log_with_imprecise_labels, \
    apply_im_without_noise
from clustering_variant import ClusteringVariant
from distance_metrics import DistanceVariant
from file_writer_helper import get_config_string, write_summary_file, \
    write_summary_file_with_parameters, run_start_string
from goldenstandardmodel import GoldenStandardModel, export_models_and_pngs
from label_splitter_multi_layer_igraph import LabelSplitter
from pipeline_helpers_shared import get_xixi_metrics, get_tuples_for_folder
from pipeline_runner_single_layer_networkx import get_imprecise_labels
from pipeline_variant import PipelineVariant, remove_pipeline_variant_from_string
from plot_helpers import plot_noise_to_f1_score
from shared_constants import evaluated_models


def run_pipeline_multi_layer_igraph(input_models=evaluated_models) -> None:
    # apply_pipeline_to_folder([('real_logs/road_traffic_fines_N_W',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/Road_Traffic_Fine_Management_Process_shortened_labels.xes.gz')],
    #                          'real_logs.txt',
    #                          labels_to_split=['F'],
    #                          use_frequency=False)
    #
    mrt07_0946_list = get_tuples_for_folder(
        '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt07-0946/logs/',
        'mrt07-0946')

    apply_pipeline_to_folder(mrt07_0946_list[12:],
                             'mrt07-0946',
                             PipelineVariant.VARIANTS,
                             labels_to_split=[],
                             use_frequency=False,
                             use_noise=False)
    #
    # mrt05_1442_list = get_tuples_for_folder('/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_adaptive_OD/mrt05-1442/logs/', 'mrt05-1442')
    #
    # apply_pipeline_to_folder(mrt05_1442_list,
    #                          'mrt05-1442.txt',
    #                          labels_to_split=[],
    #                          use_frequency=False)
    #
    #
    # feb19_1230_list = get_tuples_for_folder('/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_IMD/feb19-1230/logs/', 'feb19-1230')
    #
    # apply_pipeline_to_folder(feb19_1230_list,
    #                          'feb19-1230.txt',
    #                          labels_to_split=[],
    #                          use_frequency=False)

    #
    # feb16_1625_list = get_tuples_for_folder('/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_OD/feb16-1625/logs/', 'feb16-1625')
    #
    # apply_pipeline_to_folder(feb16_1625_list[10:],
    #                          'feb16-1625.txt',
    #                          labels_to_split=[],
    #                          use_frequency=False)


def apply_pipeline_to_folder(input_list, folder_name, pipeline_variant, labels_to_split=[], use_frequency=False, use_noise=True):
    for (name, path) in input_list:
        best_precision, best_configs, xixi_precision, golden_standard_precision = apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(
            name,
            pipeline_variant,
            labels_to_split,
            path,
            20000000,
            use_frequency=use_frequency,
            use_noise=use_noise)
        try:
            summary_file_name = f'{folder_name}_{pipeline_variant}.txt'
            write_summary_file_with_parameters(best_configs, best_precision, name, summary_file_name)
            write_summary_file(best_precision, golden_standard_precision, name, summary_file_name,
                                         xixi_precision)
        except Exception as e:
            print('----------------Exception occurred------------------------')
            print(e)
            with open(f'./outputs/best_results/{summary_file_name}', 'a') as outfile:
                outfile.write(f'´\n----------------Exception occurred------------------------\n')
                outfile.write(f'{repr(e)}\n')
            continue


def apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(input_name: str,
                                                                      pipeline_variant: PipelineVariant,
                                                                      labels_to_split: List[str],
                                                                      log_path: str,
                                                                      max_number_of_traces: int,
                                                                      use_frequency=False,
                                                                      use_noise=True):
    input_name = f'{input_name}_{pipeline_variant}' if use_frequency else f'{input_name}_{pipeline_variant}_N_W'
    original_log = xes_importer.apply(log_path)

    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        print(f'Starting pipeline for {input_name}')
        outfile.write(run_start_string())

    xixi_precision = 0
    golden_standard_precision = 0

    if not labels_to_split:
        labels_to_split = get_imprecise_labels(original_log)
        xixi_precision = get_xixi_metrics(input_name, log_path, labels_to_split)

        golden_standard_model = GoldenStandardModel(input_name, '', log_path, labels_to_split)
        golden_standard_precision = golden_standard_model.evaluate_golden_standard_model()
        print('golden_standard_precision')
        print(golden_standard_precision)

        export_model_from_original_log_with_precise_labels(input_name, log_path, use_noise)

    y_f1_scores_unrefined = write_data_from_original_log_with_imprecise_labels(input_name, original_log, use_noise)

    if max_number_of_traces < 20000000:
        log = xes_importer.apply(
            log_path,
            parameters={
                xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: max_number_of_traces})
        xes_exporter.apply(log, f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_used_log.xes')

    best_precision = 0
    best_configs = []
    y_f1_scores_refined = []
    x_noises = [0, 0.1, 0.2, 0.3, 0.4]

    for label in labels_to_split:
        for window_size in [3]:
            for distance in [DistanceVariant.MULTISET_DISTANCE]:
                for threshold in [0]:
                    try:
                        log = xes_importer.apply(
                            log_path,
                            parameters={
                                xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: max_number_of_traces})

                        precision, f1_scores_refined = apply_pipeline_multi_layer_igraph_to_log(input_name,
                                                                                                pipeline_variant,
                                                                                                log,
                                                                                                [label],
                                                                                                original_log=original_log,
                                                                                                threshold=threshold,
                                                                                                window_size=window_size,
                                                                                                number_of_traces=max_number_of_traces,
                                                                                                distance_variant=distance,
                                                                                                original_log_path=log_path,
                                                                                                best_precision=best_precision,
                                                                                                use_frequency=use_frequency,
                                                                                                use_noise=use_noise)
                        if len(f1_scores_refined) > 0:
                            y_f1_scores_refined = f1_scores_refined

                        if precision > best_precision:
                            best_configs = [get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                              distance,
                                                              labels_to_split,
                                                              max_number_of_traces,
                                                              log_path,
                                                              threshold,
                                                              window_size,
                                                              use_frequency=use_frequency)]
                            best_precision = precision
                        elif round(precision, 2) == round(best_precision, 2):
                            best_configs.append(
                                get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                  distance,
                                                  labels_to_split,
                                                  max_number_of_traces,
                                                  log_path,
                                                  threshold,
                                                  window_size,
                                                  use_frequency=use_frequency))
                    except Exception as e:
                        print('----------------Exception occurred------------------------')
                        print(e)
                        with open(f'./outputs/{input_name}.txt', 'a') as outfile:
                            outfile.write(f'´\n----------------Exception occurred------------------------\n')
                            outfile.write(f'{repr(e)}\n')
                        continue

    print('best_precision of all iterations:')
    print(best_precision)

    if len(y_f1_scores_refined) > 0:
        plot_noise_to_f1_score(x_noises, y_f1_scores_unrefined, y_f1_scores_refined, input_name)
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write('Best precision found:\n')
        outfile.write(str(best_precision))
    return best_precision, best_configs, xixi_precision, golden_standard_precision


def export_model_from_original_log_with_precise_labels(input_name, path, use_noise=True):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write('\n Data from log without imprecise labels\n')
        original_input_name = remove_pipeline_variant_from_string(input_name)
        original_input_name = re.sub(r'.*/', '', original_input_name)

        pattern = original_input_name + r'.*'
        log_path = re.sub(pattern, f'{original_input_name}_Log.xes.gz', path)
        original_log = xes_importer.apply(log_path)
        if use_noise:
            apply_im_with_noise_and_export(input_name, 'original_log_precise_labels', original_log, original_log, outfile)
        apply_im_without_noise_and_export(input_name, 'original_log_precise_labels', original_log, original_log, outfile)


def apply_pipeline_multi_layer_igraph_to_log(input_name: str,
                                             pipeline_variant: PipelineVariant,
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
                                             use_frequency=False,
                                             use_noise=True
                                             ):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write(get_config_string(clustering_variant, distance_variant, labels_to_split, number_of_traces,
                                        original_log_path, threshold, window_size, use_frequency))

        label_splitter = LabelSplitter(outfile,
                                       labels_to_split,
                                       threshold=threshold,
                                       window_size=window_size,
                                       distance_variant=distance_variant,
                                       clustering_variant=clustering_variant,
                                       use_frequency=use_frequency)
        split_log = label_splitter.split_labels(log)

        outfile.write('\nPerformance split_log:\n')
        outfile.write('\nIM without threshold:\n')

        labels_to_original = label_splitter.get_split_labels_to_original_labels()

        final_marking, initial_marking, final_net, precision = apply_im_without_noise(labels_to_original, split_log, original_log,
                                                                                      outfile)

        f1_scores_refined = []
        if precision > best_precision:
            print(f'\nHigher Precision found: {precision}')

            if use_noise:
                outfile.write('\nIM with noise threshold:\n')
                f1_scores_refined = apply_im_with_noise_and_export(input_name, 'split_log', split_log, original_log,
                                                                   outfile,
                                                                   label_splitter.get_split_labels_to_original_labels())

            xes_exporter.apply(split_log,
                               f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_split_log.xes')

            tree = inductive_miner.apply_tree(split_log)
            export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_name, 'split_log')
        return precision, f1_scores_refined
