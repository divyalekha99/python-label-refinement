from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog

import clustering_variant
from apply_im import apply_im_with_noise_and_export, apply_im_without_noise
from distance_metrics import DistanceVariant
from file_writer_helper import get_config_string, write_summary_file, \
    write_summary_file_with_parameters, run_start_string
from goldenstandardmodel import export_models_and_pngs
from input_data import InputData
from input_preprocessor import InputPreprocessor
from label_splitter_event_based_igraph import LabelSplitter as LabelSplitterEventBased
from label_splitter_variant_based_igraph import LabelSplitter as LabelSplitterVariantBased
from label_splitter_variant_multiplex import LabelSplitter as LabelSplitterVariantMultiplex
from pipeline_helpers_shared import get_tuples_for_folder
from pipeline_variant import PipelineVariant
from plot_helpers import plot_noise_to_f1_score
from shared_constants import evaluated_models


def run_pipeline_multi_layer_igraph(input_models=evaluated_models) -> None:
    # apply_pipeline_to_folder([('real_logs/hospital_billing',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/Hospital_billing_event_log_shortened_labels.xes.gz')],
    #                          'real_logs.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['6'],
    #                          use_frequency=True,
    #                          use_noise=False)
    # bpmn_graph = pm4py.read_bpmn(f'/home/jonas/repositories/pm-label-splitting/bpmn_files/loop_example_th_0.bpmn')
    # log_generator = LogGenerator()
    # log = log_generator.get_log_from_bpmn(bpmn_graph)
    #
    # net_a, im_a, fm_a = bpmn_converter.apply(bpmn_graph)
    #
    # net_b, im_b, fm_b = inductive_miner.apply(log)
    #
    # model_comparer = ModelComparer(net_a, im_a, fm_a, net_b, im_b, fm_b, log, '', 0)
    # precision, recall = model_comparer.compare_models()
    # print('final precision')
    # print(precision)
    # print('final recall')
    # print(recall)

    feb16_1625_list = get_tuples_for_folder(
        '/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_OD/feb16-1625/logs/',
        'feb16-1625')

    apply_pipeline_to_folder(feb16_1625_list[1:],
                             'feb16-1625.txt',
                             PipelineVariant.VARIANTS,
                             labels_to_split=[],
                             use_frequency=True,
                             use_noise=False)

    # apply_pipeline_to_folder(feb16_1625_list[-2:],
    #                          'feb16-1625.txt',
    #                          PipelineVariant.EVENTS,
    #                          labels_to_split=[],
    #                          use_frequency=True,
    #                          use_noise=False)

    # apply_pipeline_to_folder([('real_logs/road_traffic_fines',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/Road_Traffic_Fine_Management_Process_shortened_labels.xes.gz')],
    #                          'real_logs.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['F'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # apply_pipeline_to_folder([('real_logs/BPI_Challenge_2017_N_W',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/BPI_Challenge_2017_shortened_labels.xes.gz')],
    #                          'real_logs.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['e'],
    #                          use_frequency=False,
    #                          use_noise=False)
    #
    # mrt07_0946_list = get_tuples_for_folder(
    #     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt07-0946/logs/',
    #     'mrt07-0946')
    #
    # apply_pipeline_to_folder(mrt07_0946_list[15:],
    #                          'mrt07-0946',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=[],
    #                          use_frequency=False,
    #                          use_noise=False)

    # mrt05_1442_list = get_tuples_for_folder('/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_adaptive_OD/mrt05-1442/logs/', 'mrt05-1442')
    #
    # apply_pipeline_to_folder(mrt05_1442_list,
    #                          'mrt05-1442.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=[],
    #                          use_frequency=False,
    #                          use_noise=False)
    #
    #

    #
    # feb19_1230_list = get_tuples_for_folder('/home/jonas/repositories/pm-label-splitting/example_logs/noImprInLoop_default_IMD/feb19-1230/logs/', 'feb19-1230')
    #
    # apply_pipeline_to_folder(feb19_1230_list,
    #                          'feb19-1230.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=[],
    #                          use_frequency=True,
    #                          use_noise=False)


def apply_pipeline_to_folder(input_list, folder_name, pipeline_variant, labels_to_split=[], use_frequency=False,
                             use_noise=True):
    for (name, path) in input_list:
        input_data = InputData(original_input_name=name,
                               log_path=path,
                               pipeline_variant=pipeline_variant,
                               labels_to_split=labels_to_split,
                               use_frequency=use_frequency,
                               use_noise=use_noise,
                               max_number_of_traces=20000000)

        input_data.original_log = xes_importer.apply(input_data.log_path, parameters={
            xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: input_data.max_number_of_traces})
        input_data.input_name = f'{input_data.original_input_name}_{input_data.pipeline_variant}' if use_frequency else f'{input_data.original_input_name}_{input_data.pipeline_variant}_N_W'

        input_preprocessor = InputPreprocessor(input_data)
        input_preprocessor.preprocess_input()

        best_combined_score, best_configs = apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(
            input_data)
        try:
            summary_file_name = f'{folder_name}_{pipeline_variant}.txt' if use_frequency else f'{folder_name}_{pipeline_variant}_N_W.txt'
            write_summary_file_with_parameters(best_configs, best_combined_score, name, summary_file_name)
            write_summary_file(best_combined_score, input_data.ground_truth_precision, name, summary_file_name,
                               input_data.xixi_precision)
        except Exception as e:
            print('----------------Exception occurred------------------------')
            print(e)
            with open(f'./outputs/best_results/{summary_file_name}', 'a') as outfile:
                outfile.write(f'´\n----------------Exception occurred------------------------\n')
                outfile.write(f'{repr(e)}\n')
            continue


def apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(input_data: InputData):
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        print(f'Starting pipeline for {input_data.input_name}')
        outfile.write(run_start_string())

    if input_data.max_number_of_traces < 20000000:
        log = xes_importer.apply(
            input_data.log_path,
            parameters={
                xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: input_data.max_number_of_traces})
        xes_exporter.apply(log,
                           f'/home/jonas/repositories/pm-label-splitting/outputs/{input_data.input_name}_used_log.xes')

    best_precision = 0
    best_configs = []
    y_f1_scores_refined = []
    x_noises = [0, 0.1, 0.2, 0.3, 0.4]

    for label in input_data.labels_to_split:
        for window_size in [2, 3, 4]:
            for distance in [DistanceVariant.EDIT_DISTANCE,
                             DistanceVariant.SET_DISTANCE,
                             DistanceVariant.MULTISET_DISTANCE]:
                for threshold in [0, 0.25, 0.5, 0.75]:
                    try:
                        log = xes_importer.apply(
                            input_data.log_path,
                            parameters={
                                xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: input_data.max_number_of_traces})

                        combined_score, f1_scores_refined = apply_pipeline_multi_layer_igraph_to_log(input_data, log,
                                                                                                     distance,
                                                                                                     window_size,
                                                                                                     threshold,
                                                                                                     best_precision)
                        if len(f1_scores_refined) > 0:
                            y_f1_scores_refined = f1_scores_refined

                        if combined_score > best_precision:
                            best_configs = [get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                              distance,
                                                              input_data.labels_to_split,
                                                              input_data.max_number_of_traces,
                                                              input_data.log_path,
                                                              threshold,
                                                              window_size,
                                                              use_frequency=input_data.use_frequency)]
                            best_precision = combined_score
                        elif round(combined_score, 2) == round(best_precision, 2):
                            best_configs.append(
                                get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                  distance,
                                                  input_data.labels_to_split,
                                                  input_data.max_number_of_traces,
                                                  input_data.log_path,
                                                  threshold,
                                                  window_size,
                                                  use_frequency=input_data.use_frequency))
                    except Exception as e:
                        print('----------------Exception occurred------------------------')
                        print(e)
                        with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
                            outfile.write(f'´\n----------------Exception occurred------------------------\n')
                            outfile.write(f'{repr(e)}\n')
                        continue

    print('best_precision of all iterations:')
    print(best_precision)

    if len(y_f1_scores_refined) > 0:
        plot_noise_to_f1_score(x_noises, input_data.y_f1_scores_unrefined, y_f1_scores_refined, input_data.input_name)
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write('Best precision found:\n')
        outfile.write(str(best_precision))
    return best_precision, best_configs


def apply_pipeline_multi_layer_igraph_to_log(input_data: InputData,
                                             log: EventLog,
                                             distance_variant: DistanceVariant,
                                             window_size: int,
                                             threshold: float,
                                             best_precision: float):
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write(get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION, distance_variant,
                                        input_data.labels_to_split, input_data.max_number_of_traces,
                                        input_data.log_path, threshold, window_size, input_data.use_frequency))

        if input_data.pipeline_variant == PipelineVariant.VARIANTS:
            label_splitter = LabelSplitterVariantBased(outfile,
                                                       input_data.labels_to_split,
                                                       threshold=threshold,
                                                       window_size=window_size,
                                                       distance_variant=distance_variant,
                                                       clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                       use_frequency=input_data.use_frequency)
        elif input_data.pipeline_variant == PipelineVariant.VARIANTS_MULTIPLEX:
            label_splitter = LabelSplitterVariantMultiplex(outfile,
                                                           input_data.labels_to_split,
                                                           threshold=threshold,
                                                           window_size=window_size,
                                                           distance_variant=distance_variant,
                                                           clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                           use_frequency=input_data.use_frequency)
        else:
            label_splitter = LabelSplitterEventBased(outfile,
                                                     input_data.labels_to_split,
                                                     threshold=threshold,
                                                     window_size=window_size,
                                                     distance_variant=distance_variant,
                                                     clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION)

        split_log = label_splitter.split_labels(log)

        outfile.write('\nPerformance split_log:\n')
        outfile.write('\nIM without threshold:\n')

        labels_to_original = label_splitter.get_split_labels_to_original_labels()

        final_marking, initial_marking, final_net, precision = apply_im_without_noise(labels_to_original,
                                                                                      split_log,
                                                                                      input_data.original_log,
                                                                                      outfile,
                                                                                      label_splitter.short_label_to_original_label)

        f1_scores_refined = []
        # model_comparer = ModelComparer(golden_net, golden_im, golden_fm, final_net, initial_marking, final_marking,
        #                                original_log, outfile, 0)
        # s_precision, s_recall = model_comparer.compare_models()

        if precision > best_precision:
            print(f'\nHigher Precision found: {precision}')

            if input_data.use_noise:
                outfile.write('\nIM with noise threshold:\n')
                f1_scores_refined = apply_im_with_noise_and_export(input_data.input_name, 'split_log', split_log,
                                                                   input_data.original_log,
                                                                   outfile,
                                                                   label_splitter.get_split_labels_to_original_labels(),
                                                                   label_splitter.short_label_to_original_label)

            xes_exporter.apply(split_log,
                               f'/home/jonas/repositories/pm-label-splitting/outputs/{input_data.input_name}_split_log.xes')

            tree = inductive_miner.apply_tree(split_log)
            export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_data.input_name, 'split_log')
        return precision, f1_scores_refined
