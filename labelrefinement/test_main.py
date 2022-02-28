import copy as c
import csv
import os
import sys
from pathlib import Path
from time import time

from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.log.importer.xes import importer as xes_import_factory
from pm4py.objects.process_tree.importer import importer as ptml_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner


import test_epoch

log_size_parameter = int(sys.argv[1])
# number_of_cores = int(sys.argv[2])
batch_size_parameter = int(sys.argv[2])  # max 610
experiment_nr_parameter = int(sys.argv[3])  # max 610
start_data_set_size_parameter = int(sys.argv[4])  # max 610


# end_data_set_size_parameter = int(sys.argv[4])  # max 610

def main():
    # directory = "xixi_files/noImprInLoop_default_OD" 23937<
    directory = "../../../data/noImprInLoop_default_OD"
    # directory = "../../../data/test"

    data = {}
    setting_ids = []
    for folder_name in (os.listdir(directory)):
        log_folder_list = os.listdir(os.path.join(directory, folder_name, "logs"))

        for file_name in log_folder_list:
            setting_id = '_'.join(file_name.split("_")[:2])
            if setting_id not in setting_ids:
                setting_ids.append((setting_id, folder_name))
                data[(setting_id, folder_name)] = {}

    m = 0

    for folder_name in os.listdir(directory):
        log_folder_list = os.listdir(os.path.join(directory, folder_name, "logs"))
        model_folder_list = os.listdir(os.path.join(directory, folder_name, "models"))
        for log_file_name in log_folder_list:
            setting = ('_'.join(log_file_name.split("_")[:2]), folder_name)
            data[setting]["setting"] = setting  # TODO change data dictionary to list
            if "LogR" in log_file_name:
                data[setting]["xixi_log_path"] = os.path.join(directory, folder_name, "logs", log_file_name)
            if "LogD" in log_file_name:
                # print('Test')
                data[setting]["event_log_path"] = os.path.join(directory, folder_name, "logs", log_file_name)
            if "LogR" not in log_file_name and "LogD" not in log_file_name:
                # print('Ping')
                data[setting]["original_log_path"] = os.path.join(directory, folder_name, "logs", log_file_name)

        for model_file_name in model_folder_list:
            m = m + 1
            # setting = (model_file_name[0] + "1", folder_name) #todo dangerous
            setting = ('_'.join(model_file_name.split("_")[0]) + "1", folder_name)  # todo dangerous
            if setting in data.keys():
                data[setting]["model_path"] = os.path.join(directory, folder_name, "models", model_file_name)

    Path('../results/exp_' + str(experiment_nr_parameter)).mkdir(parents=True, exist_ok=True)
    Path('../results/exp_' + 'xixi_cd_' + str(experiment_nr_parameter)).mkdir(parents=True, exist_ok=True)
    Path('../results/exp_' + 'xixi_cc_' + str(experiment_nr_parameter)).mkdir(parents=True, exist_ok=True)

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

    if Path('../results/exp_' + 'xixi_cc_' + str(experiment_nr_parameter) + "/result_" + str(
            start_data_set_size_parameter) + '.csv').is_file() or Path(
        '../results/exp_' + 'xixi_cd_' + str(experiment_nr_parameter) + "/result_" + str(
            start_data_set_size_parameter) + '.csv').is_file():
        print('Warning: File already exists!')
        return

    with open(
            '../results/exp_' + 'xixi_cc_' + str(experiment_nr_parameter) + "/result_" + str(
                start_data_set_size_parameter) + '.csv',
            'w') as csvfile:
        fwriter = csv.writer(csvfile)
        fwriter.writerow(header)

    with open(
            '../results/exp_' + 'xixi_cd_' + str(experiment_nr_parameter) + "/result_" + str(
                start_data_set_size_parameter) + '.csv',
            'w') as csvfile:
        fwriter = csv.writer(csvfile)
        fwriter.writerow(header)

    # Start from the first cell below the headers.
    row = 1
    col = 0

    # print(data)
    print(len(data))
    print("m ", m)
    data2 = c.deepcopy(data)
    for d in data:
        if len(data[d]) != 5:  # print(d)
            # print(d)
            # print(data[d])
            # print("ERRRRRRRRRRRRRRRRRRRROW")
            # del data2[d]
            pass

    ###########################
    # What does del data2[d] do?
    ##########################

    data = data2
    print("neue länge:", (len(data)))

    time1 = time()
    '''
    #from multiprocessing.pool import ThreadPool as ThreadPool

    from multiprocessing import Pool as ThreadPool
    pool = ThreadPool(number_of_cores)
    #results = pool.imap(inside_function, list(data.values())[:end_data_set_size_parameter])
    #    results = pool.map_async(inside_function, list(data.values())[:data_set_size_parameter]).get()


    #results = [pool.apply_async(inside_function, t) for t in used_data]
    #results = pool.map(inside_function, data.values())

    pool.close()
    pool.join()

    '''
    # print("position in files: ", list(data.values())[start_data_set_size_parameter:start_data_set_size_parameter+15])
    print(list(data.values())[start_data_set_size_parameter * batch_size_parameter:(start_data_set_size_parameter + 1) * batch_size_parameter])

    results = [inside_function(d) for d in list(data.values())[start_data_set_size_parameter * batch_size_parameter:(start_data_set_size_parameter + 1) * batch_size_parameter]]

    time2 = time()
    print("overalltime: ", time2 - time1)

    # print(list(results))
    # Path('../results/exp_' + str(experiment_nr_parameter)).mkdir(parents=True, exist_ok=True)
    # with open('../results/exp_' + str(experiment_nr_parameter) + "/result_" + str(start_data_set_size_parameter) + '.csv', 'w') as csvfile:
    #     fwriter = csv.writer(csvfile)
    #     fwriter.writerow(("log", "folder", \
    #           "org_model_prec", "precise_refined_log_prec",\
    #         "imp_prec", "xixi_prec", "ref_log_prec",\
    #         "ref_log_comdec_prec", "ref_log_folding_prec", "ref_log_semi_prec", "ref_log_no_vertical_prec",\
    #         "ref_log_all_prec",\
    #         "ref_log_no_comdec_prec", "ref_log_no_folding_prec", "ref_log_no_semi_prec", "ref_log_vertical_prec",\
    #         "number_of_different_original_labels", \
    #         "epoch_time",\
    #         "time_needed_for_all_extensions", \
    #         "time_for_greedy_mapping", "time_for_semi_greedy_mapping", \
    #         "num_of_new_labels", "num_of_new_labels_comdec", "num_of_new_labels_folding", "num_of_new_labels_semi", "num_of_new_labels_no_vertical", \
    #         "mapping_quality", "mapping_folding_quality", "mapping_semi_quality", "mapping_folding_semi_quality"))
    #     for x in results:
    #         fwriter.writerow(x)


def inside_function(paths):
    print('Inside called')
    log_size = log_size_parameter
    print(paths.keys)
    if "event_log_path" in paths.keys() and "original_log_path" in paths.keys():
        print('in if')
        # print("setting: ", setting)
        event_log = xes_import_factory.apply(paths["event_log_path"], parameters={
            xes_import_factory.Variants.ITERPARSE.value.Parameters.MAX_TRACES: log_size})

        xixi_log = xes_import_factory.apply(paths["xixi_log_path"], parameters={
            xes_import_factory.Variants.ITERPARSE.value.Parameters.MAX_TRACES: log_size}) if 'xixi_log_path' in paths.keys() and paths['xixi_log_path'] else None
        print(paths["original_log_path"])
        original_event_log = xes_import_factory.apply(paths["original_log_path"], parameters={
            xes_import_factory.Variants.ITERPARSE.value.Parameters.MAX_TRACES: log_size})

        if 'model_path' in paths.keys() and paths['model_path']:
            original_tree = ptml_importer.apply(paths["model_path"])
            original_net, original_initial_marking, original_final_marking = pt_converter.apply(original_tree)
        else:
            original_net, original_initial_marking, original_final_marking = inductive_miner.apply(original_event_log)
        print(original_net)

        time0 = time()
        print('experiment_nr_parameter')
        print(experiment_nr_parameter)

        org_model_prec, precise_refined_log_prec, \
        imp_prec, xixi_prec, ref_log_prec, \
        ref_log_comdec_prec, ref_log_folding_prec, ref_log_semi_prec, ref_log_no_vertical_prec, \
        ref_log_all_prec, \
        ref_log_no_comdec_prec, ref_log_no_folding_prec, ref_log_no_semi_prec, ref_log_vertical_prec, \
        number_of_different_original_labels, \
        epoch_time, \
        time_needed_for_all_extensions, \
        time_for_greedy_mapping, time_for_semi_greedy_mapping, \
        num_of_new_labels, num_of_new_labels_comdec, num_of_new_labels_folding, num_of_new_labels_semi, num_of_new_labels_no_vertical, \
        mapping_quality, mapping_folding_quality, mapping_semi_quality, mapping_folding_semi_quality \
            = test_epoch.run(event_log, xixi_log, original_event_log, original_net, original_initial_marking,
                             original_final_marking, experiment_nr_parameter, start_data_set_size_parameter,
                             paths["setting"][0], paths["setting"][1],
                             use_adaptive_parameters=False)
        time1 = time()
        # print("time not adaptive: ", time1 - time0)
        '''
        org_model_prec, precise_refined_log_prec, \
        imp_prec, xixi_prec, ref_log_prec, \
        ref_log_comdec_prec, ref_log_folding_prec, ref_log_semi_prec, ref_log_postprocessing_prec, \
        ref_log_all_prec, \
        ref_log_no_comdec_prec, ref_log_no_folding_prec, ref_log_no_semi_prec, ref_log_no_postprocessing_prec, \
        number_of_different_original_labels = test_epoch.run(event_log, xixi_log, original_event_log, original_net,
                                                            original_initial_marking, original_final_marking, use_adaptive_parameters=True)
        time2 = time()
        print("time adaptive: ", time2 - time1)
        '''
        print(paths["setting"][0], paths["setting"][1], \
              org_model_prec, precise_refined_log_prec, \
              imp_prec, xixi_prec, ref_log_prec, \
              ref_log_comdec_prec, ref_log_folding_prec, ref_log_semi_prec, ref_log_no_vertical_prec, \
              ref_log_all_prec, \
              ref_log_no_comdec_prec, ref_log_no_folding_prec, ref_log_no_semi_prec, ref_log_vertical_prec, \
              number_of_different_original_labels, \
              epoch_time, \
              time_needed_for_all_extensions, \
              time_for_greedy_mapping, time_for_semi_greedy_mapping, \
              num_of_new_labels, num_of_new_labels_comdec, num_of_new_labels_folding, num_of_new_labels_semi,
              num_of_new_labels_no_vertical, \
              mapping_quality, mapping_folding_quality, mapping_semi_quality, mapping_folding_semi_quality
              )

        return paths["setting"][0], paths["setting"][1], \
               org_model_prec, precise_refined_log_prec, \
               imp_prec, xixi_prec, ref_log_prec, \
               ref_log_comdec_prec, ref_log_folding_prec, ref_log_semi_prec, ref_log_no_vertical_prec, \
               ref_log_all_prec, \
               ref_log_no_comdec_prec, ref_log_no_folding_prec, ref_log_no_semi_prec, ref_log_vertical_prec, \
               number_of_different_original_labels, \
               epoch_time, \
               time_needed_for_all_extensions, \
               time_for_greedy_mapping, time_for_semi_greedy_mapping, \
               num_of_new_labels, num_of_new_labels_comdec, num_of_new_labels_folding, num_of_new_labels_semi, num_of_new_labels_no_vertical, \
               mapping_quality, mapping_folding_quality, mapping_semi_quality, mapping_folding_semi_quality


main()
