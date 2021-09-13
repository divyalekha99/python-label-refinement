import json
import string
from itertools import combinations
from typing import TextIO, Set

import editdistance as editdistance
import networkx as nx
import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from networkx import Graph
from numpy import integer
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
import networkx as nx

from clustering_variant import ClusteringVariant
from distance_metrics import DistanceVariant, DistanceCalculator


class LabelSplitter:
    # (Second functionality: Label split log)
    # Input: Event log
    # Output: Event log with split labels
    # Optional Parameters: list_of_labels, Similarity threshold, window / horizon size, suffix / prefix weight
    # Option to generate both split logs (my approach + other approach)
    # Window size
    # calculate edit distance between all events
    # Iterate over each event with window / horizon size
    # Use editdistance library (should be efficient implementation)
    # -> Save in data structure
    # Generate a graph with the events connected that pass a certain threshold
    # Or generate a graph that contains the distance
    # Use community detection or other heuristic to find labels that should be split
    # Generate new event log with split events

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
        self.hash_to_event = {}
        self.distance_variant = distance_variant
        self.distance_calculator = DistanceCalculator(window_size)
        self.clustering_variant = clustering_variant

        if distance_variant is DistanceVariant.EDIT_DISTANCE:
            self.get_distance = self.distance_calculator.get_edit_distance
        elif distance_variant is DistanceVariant.SET_DISTANCE:
            self.get_distance = self.distance_calculator.get_set_distance
        elif distance_variant is DistanceVariant.MULTISET_DISTANCE:
            self.get_distance = self.distance_calculator.get_multiset_distance
        else:
            print('Warning: Distance metric not found, fallback to default distance')
            self.get_distance = self.get_edit_distance

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
        self.get_connected_components(event_graphs=event_graphs)
        self.get_communities_louvain(event_graphs=event_graphs)
        self.set_split_labels(event_graphs, log)

        return log
        #       variants = variants_filter.get_variants(log)

        #        self._write('Variants')
        #       for variant in variants:
        #          self._write(variants[variant])
        #         self._write(len(variants[variant]))
        #    self._write(variants.keys())
        # filtered_keys = [key.replace(',', '') for key in variants.keys()]
        # self._write(filtered_keys)

    def get_event_graphs_from_event_log(self, log) -> dict[str, Graph]:
        event_graphs = {}
        for case_id, trace in enumerate(log):
            # self._write('trace')
            # self._write(trace)
            # self._write(trace['attributes']['concept:name'])
            prefix = ''
            processed_events = []
            for position, event in enumerate(trace):
                label = event['concept:name']

                event['case_id'] = case_id
                event['position'] = position
                if label not in list(event_graphs.keys()) and label in self.labels_to_split:
                    event_graphs[label] = nx.Graph()

                for preceding_event in processed_events:
                    # self._write('Event:')
                    # self._write(preceding_event)
                    preceding_event['suffix'] = preceding_event['suffix'] + label

                event['prefix'] = prefix
                event['suffix'] = ''
                event['label'] = label
                processed_events.append(event)

                # graph.add_node(event, prefix=prefix, suffix='')
                prefix = prefix + label
                # self._write(event)
            for event in processed_events:
                label = event['concept:name']
                if label in self.labels_to_split:
                    self.hash_to_event[hash(event)] = event
                    event_graphs[label].add_node(hash(event))
        print('Finished calculating event_graphs')
        return event_graphs

    def calculate_edges(self, event_graphs) -> None:
        i = 0
        for (label, graph) in event_graphs.items():
            print(f'Calculating edges for {label}')
            # self._write(label)
            print(len(graph.nodes()))
            edges = []
            # TODO Check performance of combinations
            for (hash_a, hash_b) in combinations(graph.nodes(), 2):
                if i % 100000 == 0:
                    print(i)
                # edit_distance = self.get_edit_distance(self.hash_to_event[hash_a], self.hash_to_event[hash_b])
                edit_distance = self.get_distance(self.hash_to_event[hash_a], self.hash_to_event[hash_b])
                weight = 1 - edit_distance / self.window_size
                # print(weight)
                # self._write('weight')
                # self._write(weight)
                if weight > self.threshold:
                    # TODO Try adding multiple edges at once
                    # Try first fully connected graph, then edges?
                    edges.append((hash_a, hash_b, weight))
                    # graph.add_edge(hash_a, hash_b, weight=weight)
                    # self._write(edit_distance)
                i += 1
            graph.add_weighted_edges_from(edges)
        print('Finished calculating edges')

    def get_communities_louvain(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            print(f'Getting communities for {label}')
            partition = community_louvain.best_partition(graph, weight="weight", randomize=False)
            # self._write('Partition:')
            # self._write(partition)

            for community in partition.values():
                self._split_labels_to_original_labels[f'{label}_{community}'] = label

            for hash_value in graph.nodes:
                self.hash_to_event[hash_value]['label'] = f'{label}_{partition[hash_value]}'
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

    def set_split_labels(self, event_graphs, log):
        for label in self.labels_to_split:
            # temp = list(filter(lambda event: event['label'] == f'{label}_0', event_graphs[label].nodes))
            for hash_value in event_graphs[label].nodes:
                # TODO Is this really necessary or would it suffice to manipulate the hash map?
                event = self.hash_to_event[hash_value]
                log[event['case_id']][event['position']]['concept:name'] = event['label']
        print('Finished setting labels')

    def get_connected_components(self, event_graphs) -> None:
        self._write('Connected components:')
        for (label, graph) in event_graphs.items():
            if label != 'Payment':
                continue
            self._write(label)
            self._write(str(nx.is_connected(graph)))
            self._write(str(nx.number_connected_components(graph)))
            self._write(''.join([str(len(c)) for c in sorted(nx.connected_components(graph), key=len, reverse=True)]))
