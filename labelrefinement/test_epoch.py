import csv
from time import time

from igraph import *
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.evaluation.generalization import evaluator as generalization_evaluator
from pm4py.evaluation.simplicity import evaluator as simplicity_evaluator

import egraph_builder
import egraph_label_refinement
import mapping_all
import mapping_modularity
import precision_util


def has_duplicate_xor(net, imprecise_labels, original_labels):
    for transition in net.transitions:
        if transition.label != None and transition.label in original_labels:
            transition.label = imprecise_labels[0]

    for p in net.places:
        seen_labels = []
        for a in p.out_arcs:
            t = a.target
            if t.label != None and t.label in imprecise_labels and t.label in seen_labels:
                return True
            seen_labels.append(t.label)
    return False


def run(event_log, xixi_log, original_event_log, original_net, original_initial_marking, original_final_marking,
        experiment_nr_parameter, start_data_set_size_parameter, log_name, folder_name,
        parameters={"TIMESTAMP_KEY": "no_timestamp", "ACTIVITY_KEY": "concept:name",
                    "EVENT_IDENTIFICATION": "Activity", "CASE_ID_KEY": 0, "LIFECYCLE_KEY": "lifecycle:transition",
                    "LIFECYCLE_MODE": "atomic", "k": 1}, weight_matched=1, weight_not_matched=10, weight_structure=1,
        k=1, basic_cost=1,
        labeling_function=egraph_label_refinement.default_labeling_function, use_adaptive_parameters=False):
    start_time = time()

    egraphs, map_egraph_ID_to_trace_IDs, map_trace_ID_to_egraph_ID = egraph_builder.get_egraphs(parameters, False,
                                                                                                event_log)

    # time_s = time()
    # egraphs_folding, map_egraph_ID_to_trace_IDs_folding, map_trace_ID_to_egraph_ID_folding = egraph_builder.get_egraphs(
    #     parameters, True, event_log)
    # time_e = time()
    # time0 = time_e - time_s

    time_s = time()
    mapping = mapping_all.get_mappings(egraphs, weight_matched, weight_not_matched, weight_structure, k, basic_cost,
                                       labeling_function, "GREEDY", False)
    time_e = time()
    time_for_greedy_mapping = time_e - time_s

    # mapping_folding = mapping_all.get_mappings(egraphs_folding, weight_matched, weight_not_matched, weight_structure, k,
    #                                            basic_cost, labeling_function, "GREEDY", False)

    # time_s = time()
    # mapping_semi = mapping_all.get_mappings(egraphs, weight_matched, weight_not_matched, weight_structure, k,
    #                                         basic_cost, labeling_function, "SEMI_GREEDY", False)
    # time_e = time()
    # time_for_semi_greedy_mapping = time_e - time_s

    # time_s = time()
    # mapping_folding_semi = mapping_all.get_mappings(egraphs_folding, weight_matched, weight_not_matched,
    #                                                 weight_structure, k, basic_cost, labeling_function, "SEMI_GREEDY",
    #                                                 False)
    # time_e = time()
    time1 = time_e - time_s

    mapping_quality = mapping_modularity.get_mapping_modularity(event_log, egraphs, map_egraph_ID_to_trace_IDs,
                                                                map_trace_ID_to_egraph_ID, mapping, labeling_function)
    # mapping_folding_quality = mapping_modularity.get_mapping_modularity(event_log, egraphs_folding,
    #                                                                     map_egraph_ID_to_trace_IDs_folding,
    #                                                                     map_trace_ID_to_egraph_ID_folding,
    #                                                                     mapping_folding, labeling_function)
    # mapping_semi_quality = mapping_modularity.get_mapping_modularity(event_log, egraphs, map_egraph_ID_to_trace_IDs,
    #                                                                  map_trace_ID_to_egraph_ID, mapping_semi,
    #                                                                  labeling_function)
    # mapping_folding_semi_quality = mapping_modularity.get_mapping_modularity(event_log, egraphs_folding,
    #                                                                          map_egraph_ID_to_trace_IDs_folding,
    #                                                                          map_trace_ID_to_egraph_ID_folding,
    #                                                                          mapping_folding_semi, labeling_function)
    # print(mapping_quality)
    # print(mapping_folding_quality)
    # print(mapping_semi_quality)
    # print(mapping_folding_semi_quality)

    ref_log, imprecise_labels, original_labels, num_of_new_labels, cl = egraph_label_refinement.get_refined_event_log(
        event_log,
        cluster_method="CONNECTED_COMPONENTS",
        detection_mode_imp_in_loop="vertical",
        egraphs=egraphs,
        mapping=mapping,
        map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
        map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
        use_adaptive_parameters=use_adaptive_parameters)

    if has_duplicate_xor(original_net, imprecise_labels, original_labels):
        print('----------------------------------- Skipped because of duplicate xor -----------------------------------')
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    org_model_prec, org_model_simplicity, org_model_generalization = precision_util.get_precision_of_original_model(original_net, original_initial_marking,
                                                                    original_final_marking, event_log, imprecise_labels,
                                                                    original_labels, parameters)  # todo test

    precise_refined_log_prec, precise_simplicity, precise_generalization = precision_util.get_precision_of_precice_log(original_event_log, event_log,
                                                                           imprecise_labels, original_labels,
                                                                           parameters)
    imp_prec, imp_simplicity, imp_generalization = precision_util.get_precision(event_log, event_log, imprecise_labels, parameters)

    ref_log_prec, ref_simplicity, ref_generalization = precision_util.get_precision(ref_log, event_log, imprecise_labels, parameters)
    xixi_prec, xixi_simplicity, xixi_generalization = precision_util.get_precision(xixi_log, event_log, imprecise_labels, parameters) if xixi_log else 0

    ground_truth_clustering = get_ground_truth_clustering_from_log(event_log, imprecise_labels, original_labels)
    print('ground_truth_clustering')
    print(ground_truth_clustering)
    print('len(ground_truth_clustering)')
    print(len(ground_truth_clustering))

    print('Before loop')


    # TODO: Add no of clusters identified

    header = [
        'Log', 'Folder', 'Original Labels',
        'Original Model Precision', 'Original Log Simplicity', 'Original Log Generalization',
        'Precise Log Precision ', 'Precise Log Simplicity', 'Precise Log Generalization',
        'Unrefined Log Precision', 'Unrefined Log Simplicity', 'Unrefined Log Generalization',
        'Xixi Log Precision', 'Xixi Log Simplicity', 'Xixi Log Generalization',
        'Variant Threshold', 'Unfolding Threshold', 'Log Size', 'Refined Log Precision',
        'Refined Log ARI', 'Refined Log Simplicity', 'Refined Log Generalization'
    ]

    # Orignal model => Model the log was generated from (Process Tree)
    # Precise Log => Generated log with precise labels
    # Unrefined Log Precision => Log with imprecise Label without refinements
    # Xixi Log => Log from Xixi (her result files)
    # Refined Log => My refined log result
    # ref_log => ????

    max_ari = 0
    ################################################################################################
    for new_variant_threshold in [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
        for new_unfolding_threshold in [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
            ref_log_cc, _, _, t_num_of_new_labels, cl = egraph_label_refinement.get_refined_event_log(event_log,
                                                                                                              cluster_method="CONNECTED_COMPONENTS",
                                                                                                              detection_mode_imp_in_loop="vertical",
                                                                                                              egraphs=egraphs,
                                                                                                              mapping=mapping,
                                                                                                              variant_threshold=new_variant_threshold,
                                                                                                              unfolding_threshold=new_unfolding_threshold,
                                                                                                              map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
                                                                                                              map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
                                                                                                              use_adaptive_parameters=use_adaptive_parameters)
            ref_log_cc_precision, ref_log_cc_simplicity, ref_log_cc_generalization = precision_util.get_precision(ref_log_cc, event_log,
                                                                imprecise_labels,
                                                                parameters)

            cl = get_clustering_from_log(ref_log_cc, imprecise_labels)
            ari = compare_communities(ground_truth_clustering, cl, method='adjusted_rand')
            if ari > max_ari:  # and experiment_nr_parameter == 111
                max_ari = ari
                xes_exporter.apply(ref_log_cc, './example_loop_cc.xes')

            row = [log_name, folder_name, original_labels,
                   org_model_prec, org_model_simplicity, org_model_generalization,
                   precise_refined_log_prec, precise_simplicity, precise_generalization,
                   imp_prec, imp_simplicity, imp_generalization,
                   xixi_prec, xixi_simplicity, xixi_generalization,
                   new_variant_threshold,
                   new_unfolding_threshold, 500, ref_log_cc_precision,
                   ari, ref_log_cc_simplicity, ref_log_cc_generalization]
            with open(
                    '../results/exp_' + 'xixi_cc_' + str(experiment_nr_parameter) + "/result_" + str(
                        start_data_set_size_parameter) + '.csv',
                    'a') as csvfile:
                fwriter = csv.writer(csvfile)
                fwriter.writerow(row)
    print('after loop')
    print(f'Max ARI found for CC: {max_ari}')
    ################################################################################################


    max_ari = 0

    for new_variant_threshold in [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
        for new_unfolding_threshold in [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
            ref_log_cd, _, _, num_of_new_labels_comdec, cl = egraph_label_refinement.get_refined_event_log(
                event_log,
                egraphs=egraphs,
                cluster_method="COMMUNITY_DETECTION",
                detection_mode_imp_in_loop="vertical",
                mapping=mapping,
                variant_threshold=new_variant_threshold,
                unfolding_threshold=new_unfolding_threshold,
                map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
                map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
                use_adaptive_parameters=use_adaptive_parameters)
            ref_log_cd_precision, ref_log_cd_simplicity, ref_log_cd_generalization = precision_util.get_precision(ref_log_cd, event_log,
                                                                imprecise_labels,
                                                                parameters)

            clustering_cd = get_clustering_from_log(ref_log_cd, imprecise_labels)
            # print('clustering_cd')
            # print(clustering_cd)
            ari = compare_communities(ground_truth_clustering, clustering_cd, method='adjusted_rand')
            print('ari')
            print(ari)
            if ari > max_ari:  # and experiment_nr_parameter == 111
                max_ari = ari
                xes_exporter.apply(ref_log_cd, './example_loop_cd.xes')

            row = [log_name, folder_name, original_labels,
                   org_model_prec, org_model_simplicity, org_model_generalization,
                   precise_refined_log_prec, precise_simplicity, precise_generalization,
                   imp_prec, imp_simplicity, imp_generalization,
                   xixi_prec, xixi_simplicity, xixi_generalization,
                   new_variant_threshold, new_unfolding_threshold, 500, ref_log_cd_precision,
                   ari, ref_log_cd_simplicity, ref_log_cd_generalization]

            with open(
                    '../results/exp_' + 'xixi_cd_' + str(experiment_nr_parameter) + "/result_" + str(
                        start_data_set_size_parameter) + '.csv',
                    'a') as csvfile:
                fwriter = csv.writer(csvfile)
                fwriter.writerow(row)

    print(f'Max ARI found for CD: {max_ari}')

    # ref_log_folding, _, _, num_of_new_labels_folding = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                                                  cluster_method="CONNECTED_COMPONENTS",
    #                                                                                                  detection_mode_imp_in_loop="vertical",
    #                                                                                                  egraphs=egraphs_folding,
    #                                                                                                  mapping=mapping_folding,
    #                                                                                                  map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs_folding,
    #                                                                                                  map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID_folding,
    #                                                                                                  use_adaptive_parameters=use_adaptive_parameters)
    # ref_log_semi, _, _, num_of_new_labels_semi = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                                            cluster_method="CONNECTED_COMPONENTS",
    #                                                                                            detection_mode_imp_in_loop="vertical",
    #                                                                                            egraphs=egraphs,
    #                                                                                            mapping=mapping_semi,
    #                                                                                            map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
    #                                                                                            map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
    #                                                                                            use_adaptive_parameters=use_adaptive_parameters)
    # ref_log_no_vertical, _, _, num_of_new_labels_no_vertical = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                                                          cluster_method="CONNECTED_COMPONENTS",
    #                                                                                                          detection_mode_imp_in_loop="postprocessing",
    #                                                                                                          egraphs=egraphs,
    #                                                                                                          mapping=mapping,
    #                                                                                                          map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
    #                                                                                                          map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
    #                                                                                                          use_adaptive_parameters=use_adaptive_parameters)

    # print(num_of_new_labels, num_of_new_labels_comdec, num_of_new_labels_folding, num_of_new_labels_semi, num_of_new_labels_no_vertical)

    # time_s = time()
    # ref_log_all, _, _, _ = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                      cluster_method="COMMUNITY_DETECTION",
    #                                                                      detection_mode_imp_in_loop="postprocessing",
    #                                                                      egraphs=egraphs_folding,
    #                                                                      mapping=mapping_folding_semi,
    #                                                                      map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs_folding,
    #                                                                      map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID_folding,
    #                                                                      use_adaptive_parameters=use_adaptive_parameters)
    # time_e = time()
    # time2 = time_e - time_s
    # ref_log_no_comdec, _, _, _ = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                            cluster_method="CONNECTED_COMPONENTS",
    #                                                                            detection_mode_imp_in_loop="postprocessing",
    #                                                                            egraphs=egraphs_folding,
    #                                                                            mapping=mapping_folding_semi,
    #                                                                            map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs_folding,
    #                                                                            map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID_folding,
    #                                                                            use_adaptive_parameters=use_adaptive_parameters)
    # ref_log_no_folding, _, _, _ = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                             cluster_method="COMMUNITY_DETECTION",
    #                                                                             detection_mode_imp_in_loop="postprocessing",
    #                                                                             egraphs=egraphs, mapping=mapping_semi,
    #                                                                             map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs,
    #                                                                             map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID,
    #                                                                             use_adaptive_parameters=use_adaptive_parameters)
    # ref_log_no_semi, _, _, _ = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                          cluster_method="COMMUNITY_DETECTION",
    #                                                                          detection_mode_imp_in_loop="postprocessing",
    #                                                                          egraphs=egraphs_folding,
    #                                                                          mapping=mapping_folding,
    #                                                                          map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs_folding,
    #                                                                          map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID_folding,
    #                                                                          use_adaptive_parameters=use_adaptive_parameters)
    # ref_log_vertical, _, _, _ = egraph_label_refinement.get_refined_event_log(event_log,
    #                                                                           cluster_method="COMMUNITY_DETECTION",
    #                                                                           detection_mode_imp_in_loop="vertical",
    #                                                                           egraphs=egraphs_folding,
    #                                                                           mapping=mapping_folding_semi,
    #                                                                           map_egraph_ID_to_trace_IDs=map_egraph_ID_to_trace_IDs_folding,
    #                                                                           map_trace_ID_to_egraph_ID=map_trace_ID_to_egraph_ID_folding,
    #                                                                           use_adaptive_parameters=use_adaptive_parameters)

    # org_model_prec = precision_util.get_precision_of_original_model(original_net, original_initial_marking,
    #                                                                 original_final_marking, event_log, imprecise_labels,
    #                                                                 original_labels, parameters)  # todo test
    # precise_refined_log_prec = precision_util.get_precision_of_precice_log(original_event_log, event_log,
    #                                                                        imprecise_labels, original_labels,
    #                                                                        parameters)
    #
    # imp_prec = precision_util.get_precision(event_log, event_log, imprecise_labels, parameters)
    #
    # ref_log_prec = precision_util.get_precision(ref_log, event_log, imprecise_labels, parameters)
    # xixi_prec = precision_util.get_precision(xixi_log, event_log, imprecise_labels, parameters)
    #
    # ref_log_comdec_prec = precision_util.get_precision(ref_log_comdec, event_log, imprecise_labels, parameters)
    # ref_log_folding_prec = precision_util.get_precision(ref_log_folding, event_log, imprecise_labels, parameters)
    # ref_log_semi_prec = precision_util.get_precision(ref_log_semi, event_log, imprecise_labels, parameters)
    # ref_log_no_vertical_prec = precision_util.get_precision(ref_log_no_vertical, event_log, imprecise_labels,
    #                                                         parameters)

    # ref_log_all_prec = precision_util.get_precision(ref_log_all, event_log, imprecise_labels, parameters)
    #
    # ref_log_no_comdec_prec = precision_util.get_precision(ref_log_no_comdec, event_log, imprecise_labels, parameters)
    # ref_log_no_folding_prec = precision_util.get_precision(ref_log_no_folding, event_log, imprecise_labels, parameters)
    # ref_log_no_semi_prec = precision_util.get_precision(ref_log_no_semi, event_log, imprecise_labels, parameters)
    # ref_log_vertical_prec = precision_util.get_precision(ref_log_vertical, event_log, imprecise_labels,
    #                                                      parameters)  # no postpro = vetical ref.

    number_of_different_original_labels = precision_util.get_number_of_different_original_labels(event_log)
    # print("number_of_different_original_labels: ", number_of_different_original_labels)

    # time_needed_for_all_extensions = time0 + time1 + time2

    end_time = time()
    epoch_time = end_time - start_time
    print("epoch time: ", epoch_time)
    return org_model_prec, precise_refined_log_prec, \
           imp_prec, xixi_prec, ref_log_prec, \
           0, 0, 0, 0, \
           0, \
           0, 0, 0, 0, \
           number_of_different_original_labels, \
           epoch_time, \
           0, \
           time_for_greedy_mapping, 0, \
           num_of_new_labels, num_of_new_labels_comdec, 0, 0, 0, \
           mapping_quality, 0, 0, 0


def get_ground_truth_clustering_from_log(event_log, imprecise_labels, original_labels):
    clustering = []
    for trace in event_log:
        for event in trace:
            if event['concept:name'][0] in imprecise_labels:
                clustering.append(original_labels.index(event['OrgLabel']))
    clustering = Clustering(clustering)
    return clustering


def get_clustering_from_log(event_log, imprecise_labels):
    seen_labels = []
    clustering = []
    for trace in event_log:
        for event in trace:
            if event['concept:name'][0] in imprecise_labels:
                if event['concept:name'] not in seen_labels:
                    seen_labels.append(event['concept:name'])
                clustering.append(seen_labels.index(event['concept:name']))
    clustering = Clustering(clustering)
    print('clustering final')
    print(clustering)
    return clustering
