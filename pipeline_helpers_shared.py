import json
import os
import re

from igraph import Clustering, compare_communities
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog

from apply_im import apply_im_without_noise_and_export
from input_data import InputData


def get_xixi_metrics(input_name, log_path, labels_to_split, g_net, g_im, g_fm):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        original_log = xes_importer.apply(log_path)
        xixi_refined_log_path = log_path.replace('LogD', 'LogR', 1)
        if not os.path.isfile(xixi_refined_log_path):
            xixi_refined_log_path = xixi_refined_log_path.replace('LogR', 'LogR_IM', 1)

        log = xes_importer.apply(xixi_refined_log_path)

        # for trace in log:
        #     for event in trace:
        #         print('event[concept:name]')
        #         print(event['concept:name'])

        clustering = get_clustering_from_xixi_log(log, labels_to_split, outfile)

        labels_to_original = {}

        for label in labels_to_split:
            labels_to_original[label] = label

        outfile.write('\n Xixi refined log results:\n')
        precision, final_net, initial_marking, final_marking = apply_im_without_noise_and_export(input_name, 'xixi',
                                                                                                 log, original_log,
                                                                                                 outfile,
                                                                                                 labels_to_original=labels_to_original)

        outfile.write('\n Xixi clustering:\n')
        outfile.write(f'{str(clustering)}\n')
        # model_comparer = ModelComparer(g_net, g_im, g_fm, final_net, initial_marking, final_marking, log, outfile, precision)
        # s_precision, s_recall = model_comparer.compare_models()
    return precision, clustering


def get_clustering_from_xixi_log(log: EventLog, labels_to_split: list[str], outfile):
    variants = variants_filter.get_variants(log)
    clustering = []
    split_labels = []

    for variant in variants:
        filtered_log = variants_filter.apply(log, [variant])
        for event in filtered_log[0]:
            label = event['concept:name']
            if label[0] in labels_to_split:
                if label not in split_labels:
                    split_labels.append(label)
                clustering.append(split_labels.index(label))

    print('Clustering(clustering)')
    print(Clustering(clustering))
    print('split_labels')
    print(split_labels)
    outfile.write('\n Xixi split labels:\n')
    outfile.write(f'{str(split_labels)}\n')
    return Clustering(clustering)


def get_tuples_for_folder(folder_path, prefix):
    log_list = []
    identifier_pattern = f'^(\w+_\d+)'
    for f in os.listdir(folder_path):
        if 'LogD' in f:
            log_list.append((f'{prefix}/{re.match(identifier_pattern, f).group(1)}', f'{folder_path}{f}'))
    return log_list


def get_community_similarity(comm1: Clustering, comm2: Clustering, method='adjusted_rand'):
    return compare_communities(comm1, comm2, method)


def get_concurrent_labels(input_data: InputData, threshold: float = 0.85):
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        variants = variants_filter.get_variants(input_data.original_log)
        predecessor_count = {}
        successor_count = {}
        concurrent_labels = []

        for variant in variants:
            filtered_log = variants_filter.apply(input_data.original_log, [variant])
            last_label = ''
            for event in filtered_log[0]:
                label = event['concept:name']
                if not label in predecessor_count:
                    predecessor_count[label] = 0
                    successor_count[label] = 0

                if last_label:
                    if label in input_data.labels_to_split:
                        predecessor_count[last_label] += len(variants[variant])
                    if last_label in input_data.labels_to_split:
                        successor_count[label] += len(variants[variant])
                last_label = label

        labels = set(successor_count.keys()) | set(predecessor_count.keys())
        print('labels')
        print(labels)
        print('successor_count')
        print(json.dumps(successor_count))
        print('predecessor_count')
        print(json.dumps(predecessor_count))

        for label in labels:
            total_count = predecessor_count[label] + successor_count[label]
            if total_count == 0:
                continue
            directly_follows_ratio = abs((predecessor_count[label] - successor_count[label]) / total_count)
            print('label')
            print(label)
            print('directly_follows_ratio')
            print(directly_follows_ratio)
            if directly_follows_ratio < threshold and label not in input_data.labels_to_split:
                concurrent_labels.append(label)
        outfile.write('\n Concurrent labels:\n')
        outfile.write(f'{str(concurrent_labels)}\n')
    return concurrent_labels
