import json
import string
from itertools import combinations
from typing import TextIO

import community as community_louvain
import networkx as nx
from networkx import Graph

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
                 labels_to_split,
                 window_size: int = 3,
                 threshold: float = 0.75,
                 prefix_weight: float = 0.5,
                 clustering_variant=None,
                 distance_variant=DistanceVariant.EDIT_DISTANCE,
                 ):
        if clustering_variant == None:
            clustering_variant = ClusteringVariant.COMMUNITY_DETECTION
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
            self.get_distance = self.distance_calculator.get_edit_distance

    def _write(self, log_entry: string) -> None:
        self.outfile.write(f'{log_entry}\n')

    def get_split_labels_to_original_labels(self):
        self._write('Map:')
        self._write(json.dumps(self._split_labels_to_original_labels))
        return self._split_labels_to_original_labels

    def split_labels(self, log):
        print('Starting label splitting')
        event_graphs = self.get_event_graphs_from_event_log(log)

        self.calculate_edges(event_graphs)
        # self.get_connected_components(event_graphs=event_graphs)
        self.get_communities_louvain(event_graphs=event_graphs)
        self.set_split_labels(event_graphs, log)
        return log

    def get_event_graphs_from_event_log(self, log):
        event_graphs = {}
        for case_id, trace in enumerate(log):
            prefix = ''
            processed_events = []
            for position, event in enumerate(trace):
                label = event['concept:name']

                event['case_id'] = case_id
                event['position'] = position
                if label not in list(event_graphs.keys()) and label in self.labels_to_split:
                    event_graphs[label] = nx.Graph()

                for preceding_event in processed_events:
                    preceding_event['suffix'] = preceding_event['suffix'] + label

                event['prefix'] = prefix
                event['suffix'] = ''
                event['label'] = label
                processed_events.append(event)

                prefix = prefix + label
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
            print(len(graph.nodes()))
            edges = []
            # TODO Check performance of combinations
            for (hash_a, hash_b) in combinations(graph.nodes(), 2):
                if i % 100000 == 0:
                    print(i)
                edit_distance = self.get_distance(self.hash_to_event[hash_a], self.hash_to_event[hash_b])
                weight = 1 - edit_distance / self.window_size
                if weight > self.threshold:
                    edges.append((hash_a, hash_b, weight))
                i += 1
            graph.add_weighted_edges_from(edges)
        print('Finished calculating edges')

    def get_communities_louvain(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            print(f'Getting communities for {label}')
            partition = community_louvain.best_partition(graph, weight="weight", randomize=False)

            for community in partition.values():
                self._split_labels_to_original_labels[f'{label}_{community}'] = label

            for hash_value in graph.nodes:
                self.hash_to_event[hash_value]['label'] = f'{label}_{partition[hash_value]}'
            self._write('\nReassigned labels')
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
