from itertools import combinations
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

    def __init__(self, labels_to_split: list[str], window_size: int = 3, threshold: float = 0.75,
                 prefix_weight: float = 0.5):
        self.labels_to_split = labels_to_split
        self.window_size = window_size
        self.threshold = threshold
        self.prefix_weight = prefix_weight
        self._split_labels_to_original_labels = {}

    def get_split_labels_to_original_labels(self) -> dict[str, str]:
        print('Map:')
        print(self._split_labels_to_original_labels)
        return self._split_labels_to_original_labels

    def split_labels(self, log: EventLog) -> EventLog:
        event_graphs = self.get_event_graphs_from_event_log(log)

        self.calculate_edges(event_graphs)
        self.get_connected_components(event_graphs=event_graphs)
        self.get_communities_louvain(event_graphs=event_graphs)
        self.set_split_labels(event_graphs, log)

        return log
        #       variants = variants_filter.get_variants(log)

        #        print('Variants')
        #       for variant in variants:
        #          print(variants[variant])
        #         print(len(variants[variant]))
        #    print(variants.keys())
        # filtered_keys = [key.replace(',', '') for key in variants.keys()]
        # print(filtered_keys)

    def set_split_labels(self, event_graphs, log):
        for label in self.labels_to_split:
            # temp = list(filter(lambda event: event['label'] == f'{label}_0', event_graphs[label].nodes))
            for event in event_graphs[label].nodes:
                log[event['case_id']][event['position']]['concept:name'] = event['label']

    def get_communities_louvain(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            partition = community_louvain.best_partition(graph)
            print('Partition:')
            print(partition)

            for community in partition.values():
                self._split_labels_to_original_labels[f'{label}_{community}'] = label

            for event in graph.nodes:
                event['label'] = f'{label}_{partition[event]}'
                # if partitions[partition[event]]:
                #  partitions[partition[event]].append(event)
                # else:
                #  partitions[partition[event]] = [event]

            # for key in partitions.keys():
            #  print(partitions[key])
            # print(len(partitions[key]))
            print('Reassigned labels')
            print(graph.nodes)

            # pos = nx.spring_layout(graph)
            # color the nodes according to their partition
            # cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
            # nx.draw_networkx_nodes(graph, pos, partition.keys(), node_size=40,
            #                       cmap=cmap, node_color=list(partition.values()))
            # nx.draw_networkx_edges(graph, pos, alpha=0.5)
            # plt.savefig("temp.png")
            # plt.show(block=True)

    def get_connected_components(self, event_graphs) -> None:
        print('get componets')
        for (label, graph) in event_graphs.items():
            if label != 'D':
                continue
            print(label)
            print(nx.is_connected(graph))
            print(nx.number_connected_components(graph))
            print([len(c) for c in sorted(nx.connected_components(graph), key=len, reverse=True)])

    def calculate_edges(self, event_graphs) -> None:
        for (label, graph) in event_graphs.items():
            print(label)
            # TODO: Evaluate if combinations is correct here
            for (event_a, event_b) in combinations(graph.nodes(), 2):
                edit_distance = self.get_edit_distance(event_a, event_b)
                weight = 1 - edit_distance / self.window_size
                print('weight')
                print(weight)
                if weight > self.threshold:
                    graph.add_edge(event_a, event_b, weight=weight)
                    # print(edit_distance)

    def get_edit_distance(self, event_a, event_b) -> integer:
        prefix_distance = editdistance.eval(event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):],
                                            event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):])
        # print(prefix_distance)
        suffix_distance = editdistance.eval(event_a['suffix'][:min(self.window_size, len(event_a['suffix'])) - 1],
                                            event_b['suffix'][:min(self.window_size, len(event_b['suffix'])) - 1])
        # print(suffix_distance)
        return prefix_distance * 0.5 + suffix_distance * 0.5

    def get_event_graphs_from_event_log(self, log) -> dict[str, Graph]:
        event_graphs = {}
        for case_id, trace in enumerate(log):
            print('trace')
            print(trace)
            # print(trace['attributes']['concept:name'])
            prefix = ''
            processed_events = []
            for position, event in enumerate(trace):
                label = event['concept:name']

                event['case_id'] = case_id
                event['position'] = position
                if label not in list(event_graphs.keys()) and label in self.labels_to_split:
                    event_graphs[label] = nx.Graph()

                for preceding_event in processed_events:
                    print('Event:')
                    print(preceding_event)
                    preceding_event['suffix'] = preceding_event['suffix'] + label

                event['prefix'] = prefix
                event['suffix'] = ''
                event['label'] = label
                processed_events.append(event)

                # graph.add_node(event, prefix=prefix, suffix='')
                prefix = prefix + label
                print(event)
            for event in processed_events:
                label = event['concept:name']
                if label in self.labels_to_split:
                    event_graphs[label].add_node(event)
        return event_graphs
