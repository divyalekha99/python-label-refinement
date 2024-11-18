import os
import re

from igraph import Clustering, compare_communities
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
# from pm4py.objects.conversion.process_tree import converter, variants
from pm4py.objects.conversion.process_tree import converter, variants
# from pm4py.objects.conversion.process_tree import variants
# from pm4py.objects.conversion.process_tree.variants import to_petri_net
from pm4py.algo.filtering.log.variants import variants_filter

from utils.input_data import InputData
from pipeline.pipeline_variant import PipelineVariant


def get_clustering_from_xixi_log(log, labels_to_split, outfile, input_data: InputData):
    variants = variants_filter.get_variants(log)
    clustering = []
    split_labels = []

    if input_data.pipeline_variant != PipelineVariant.EVENTS:
        print('test clustering from Xixi log')
        for variant in variants:
            filtered_log = variants_filter.apply(log, [variant])
            for event in filtered_log[0]:
                label = event['concept:name']
                if label[0] in labels_to_split:
                    if label not in split_labels:
                        split_labels.append(label)
                    clustering.append(int(next(re.finditer(r'\d+$', label)).group(0)))
    else:
        print('else test clustering from Xixi log')
        for trace in log:
            for event in trace:
                label = event['concept:name']
                if label[0] in labels_to_split:
                    if label not in split_labels:
                        split_labels.append(label)
                    clustering.append(int(next(re.finditer(r'\d+$', label)).group(0)))

    outfile.write('\n Xixi split labels:\n')
    outfile.write(f'{str(split_labels)}\n')
    return Clustering(clustering)


def get_tuples_for_folder(folder_path, prefix):
    # import os
    # print("Current Working Directory:", os.getcwd())

    log_list = []
    identifier_pattern = f'^(\w+_\d+)'
    # identifier_pattern = f'^(.)'

    for f in os.listdir(folder_path):
        print("folder_path: ", f,folder_path)
        if 'LogD' in f:
        # and f.startswith('V'):
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

        for label in labels:
            total_count = predecessor_count[label] + successor_count[label]
            if total_count == 0:
                continue
            directly_follows_ratio = abs((predecessor_count[label] - successor_count[label]) / total_count)
            if directly_follows_ratio < threshold and label not in input_data.labels_to_split:
                concurrent_labels.append(label)
        outfile.write('\n Concurrent labels:\n')
        outfile.write(f'{str(concurrent_labels)}\n')
    return concurrent_labels


def filter_duplicate_xor(event_log, labels_to_split, clustering: Clustering):
    


    print('Filtering duplicate XOR transitions')

    # Apply inductive miner to get a ProcessTree
    process_tree = inductive_miner.apply(event_log)

    # Convert ProcessTree to Petri net
    # net, initial_marking, final_marking = pt_converter.apply(process_tree, variant=pt_converter.Variants.TO_PETRI_NET)
    net, initial_marking, final_marking = converter.apply(process_tree, variant= converter.Variants.TO_PETRI_NET)
    # Apply the inductive miner to the event log, generating a process tree
    # process_tree = inductive_miner.apply(event_log)

    # # Convert the process tree to a Petri net
    # net, initial_marking, final_marking = to_petri_net.apply(process_tree)


    print('Inductive miner applied')


    seen_transitions = []
    updated_label_mapping = {}
    must_update_log = False

    for t_1 in net.transitions:
        if t_1.label is not None and t_1.label[0] in labels_to_split and t_1.label not in seen_transitions:
            pre_places_1 = set()
            post_places_1 = set()
            for arc in t_1.in_arcs:
                pre_places_1.add(arc.source)
            for arc in t_1.out_arcs:
                post_places_1.add(arc.target)

            seen_transitions.append(t_1.label)
            updated_label_mapping[next(re.finditer(r'\d+$', t_1.label)).group(0)] = t_1.label

            for t_2 in net.transitions:
                if t_2.label is not None and t_2.label not in seen_transitions and t_2.label[0] in labels_to_split and t_2.label != t_1.label:
                    pre_places_2 = set()
                    post_places_2 = set()
                    for arc in t_2.in_arcs:
                        pre_places_2.add(arc.source)
                    for arc in t_2.out_arcs:
                        post_places_2.add(arc.target)

                    if pre_places_1 == pre_places_2 and post_places_1 == post_places_2:
                        print(f'Merging {t_2.label} and {t_1.label}')
                        must_update_log = True
                        seen_transitions.append(t_2.label)
                        updated_label_mapping[next(re.finditer(r'\d+$', t_2.label)).group(0)] = t_1.label

    if must_update_log:
        for trace in event_log:
            for event in trace:
                label = event['concept:name']
                if label[0] in labels_to_split:
                    event['concept:name'] = updated_label_mapping[next(re.finditer(r'\d+$', label)).group(0)]
        new_clustering = []
        for i in range(len(clustering.membership)):
            m = clustering.membership[i]
            new_m = next(re.finditer(r'\d+$', updated_label_mapping[f'{m}'])).group(0)
            new_clustering.append(int(new_m))
        clustering = Clustering(new_clustering)

    print('Updated log and clustering')

    return clustering


def get_imprecise_labels(log, real_or_synthetic):
    print('Getting imprecise labels')
    imprecise_labels = set()
    # if real_or_synthetic == 'synthetic':
    for trace in log:
        for event in trace:
            if event['OrgLabel'] != event['concept:name']:
                imprecise_labels.add(event['concept:name'])
    # else:
    #     imprecise_labels.add("Accepted In Progress")
    return list(imprecise_labels)

