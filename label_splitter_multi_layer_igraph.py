import json
import string
from itertools import combinations
from typing import TextIO

import igraph
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog

from clustering_variant import ClusteringVariant
from distance_metrics import DistanceVariant, DistanceCalculator


class LabelSplitter:
    def __init__(self,
                 outfile: TextIO,
                 labels_to_split: list[str],
                 window_size: int = 3,
                 threshold: float = 0.75,
                 prefix_weight: float = 0.5,
                 distance_variant: DistanceVariant = DistanceVariant.EDIT_DISTANCE,
                 clustering_variant: ClusteringVariant = ClusteringVariant.COMMUNITY_DETECTION):
        self.labels_to_split = labels_to_split
        self.window_size = window_size
        self.threshold = threshold
        self.prefix_weight = prefix_weight
        self._split_labels_to_original_labels = {}
        self.outfile = outfile
        self.label_and_id_to_event = {}
        self.distance_variant = distance_variant
        self.distance_calculator = DistanceCalculator(window_size)
        self.clustering_variant = clustering_variant
        self._variant_to_label = {}

        if distance_variant is DistanceVariant.EDIT_DISTANCE:
            self.get_distance = self.distance_calculator.get_edit_distance
        elif distance_variant is DistanceVariant.SET_DISTANCE:
            self.get_distance = self.distance_calculator.get_set_distance
        elif distance_variant is DistanceVariant.MULTISET_DISTANCE:
            self.get_distance = self.distance_calculator.get_multiset_distance
        else:
            print('Warning: Distance metric not found, fallback to default distance')
            self.get_distance = self.distance_calculator.get_edit_distance

    def _write(self, log_entry: string) -> None:
        self.outfile.write(f'{log_entry}\n')

    def get_split_labels_to_original_labels(self) -> dict[str, str]:
        self._write('Map:')
        self._write(json.dumps(self._split_labels_to_original_labels))
        return self._split_labels_to_original_labels

    def split_labels(self, log: EventLog) -> EventLog:
        print('Starting label splitting')
        event_graphs = self.get_event_graphs_from_event_log(log)

        self.calculate_edges(event_graphs)
        self.get_communities_louvain(event_graphs=event_graphs)
        self.set_split_labels(log)

        return log

    def get_event_graphs_from_event_log(self, log) -> dict[str, igraph.Graph]:
        variants = variants_filter.get_variants(log)
        event_graphs = {}

        # filtered_keys = [key.replace(',', '') for key in variants.keys()]
        for variant in variants:
            # print(variants[variant])
            # print(len(variants[variant]))
            # print(variants.keys())
            filtered_log1 = variants_filter.apply(log, [variant])

            prefix = ''
            processed_events = []
            occurrence_counters = {}
            for event in filtered_log1[0]:
                label = event['concept:name']
                if label not in list(event_graphs.keys()) and label in self.labels_to_split:
                    event_graphs[label] = igraph.Graph()
                    self.label_and_id_to_event[label] = []

                for preceding_event in processed_events:
                    preceding_event['suffix'] = preceding_event['suffix'] + label

                if label not in occurrence_counters:
                    occurrence_counters[label] = 0
                else:
                    occurrence_counters[label] += 1

                event['prefix'] = prefix
                event['suffix'] = ''
                event['label'] = label
                event['variant'] = label + '_' + str(variant).replace(',', '') + f'_{occurrence_counters[label]}'
                processed_events.append(event)

                # graph.add_node(event, prefix=prefix, suffix='')
                prefix = prefix + label
                # self._write(event)
            for event in processed_events:
                label = event['concept:name']
                if label in self.labels_to_split:
                    self.label_and_id_to_event[label].append(event)
                    event_graphs[label].add_vertices(1)

            for trace in filtered_log1:
                occurrence_counters = {}
                for event in trace:
                    label = event['concept:name']
                    if label not in occurrence_counters:
                        occurrence_counters[label] = 0
                    else:
                        occurrence_counters[label] += 1
                    event['variant'] = label + '_' + str(variant).replace(',', '') + f'_{occurrence_counters[label]}'

        print('Finished calculating event_graphs')
        return event_graphs

    def calculate_edges(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            print(f'Calculating edges for {label}')
            # self._write(label)
            edges = []
            weights = []
            # TODO Check performance of combinations

            print('nodes length')
            print(range(len(graph.vs) - 1))
            for (vertex_a, vertex_b) in combinations(range(len(graph.vs) - 1), 2):
                # edit_distance = self.get_edit_distance(self.hash_to_event[hash_a], self.hash_to_event[hash_b])
                edit_distance = self.get_distance(self.label_and_id_to_event[label][vertex_a],
                                                  self.label_and_id_to_event[label][vertex_b])
                weight = 1 - edit_distance / self.window_size
                # print(weight)
                if weight > self.threshold:
                    # TODO Try adding multiple edges at once
                    # Try first fully connected graph, then edges?
                    edges.append((vertex_a, vertex_b))
                    weights.append(weight)
                    # graph.add_edge(hash_a, hash_b, weight=weight)
                    # self._write(edit_distance)
            graph.add_edges(edges)
            graph.es['weight'] = weights
        print('Finished calculating edges')

    def get_communities_louvain(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            print(f'Getting communities for {label}')
            partition = graph.community_multilevel(weights=graph.es['weight'], return_levels=False)
            print(partition)

            for count, cluster in enumerate(partition):
                print('community')
                print(cluster)
                print('count')
                print(count)
                self._split_labels_to_original_labels[f'{label}_{count}'] = label
                for vertex in cluster:
                    print(vertex)
                    self.label_and_id_to_event[label][vertex]['label'] = f'{label}_{count}'
                    self._variant_to_label[self.label_and_id_to_event[label][vertex]['variant']] = f'{label}_{count}'

        # if partitions[partition[event]]:
        #  partitions[partition[event]].append(event)
        # else:
        #  partitions[partition[event]] = [event]

        # for key in partitions.keys():
        #  self._write(partitions[key])
        # self._write(len(partitions[key]))
        self._write('\nReassigned labels')
        # self._write(graph.nodes)

        # pos = nx.spring_layout(graph)
        # color the nodes according to their partition
        # cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
        # nx.draw_networkx_nodes(graph, pos, partition.keys(), node_size=40,
        #                       cmap=cmap, node_color=list(partition.values()))
        # nx.draw_networkx_edges(graph, pos, alpha=0.5)
        # plt.savefig("temp.png")
        # plt.show(block=True)

    print('Finished community detection')


    def set_split_labels(self, log):
        print('Before:')
        print(log)
        for trace in log:
            for event in trace:
                if event['variant'] in self._variant_to_label:
                    event['concept:name'] = self._variant_to_label[event['variant']]
        print('Finished setting labels')
        print(log)