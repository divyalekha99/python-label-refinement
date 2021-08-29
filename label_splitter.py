import editdistance as editdistance
from numpy import integer
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
import networkx as nx


class LabelSplitter:
    # (Second functionality: Label split log)
    # Input: Event log
    # Output: Event log with split labels
    # Optional Parameters: Similarity threshold, window / horizon size, suffix / prefix weight
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

    def __init__(self):
        pass

    def split_labels(self, log: EventLog) -> EventLog:
        event_graphs = {}

        for trace in log:
            print(trace)
            prefix = ''
            for event in trace:
                print('type:')
                print(type(event))
                label = event['concept:name']
                if label not in event_graphs.keys():
                    event_graphs[label] = nx.Graph()

                graph = event_graphs[label]
                for node in graph.nodes:
                    print('Node:')
                    print(node)
                print(graph.nodes.data())
                node['suffix'] = node['suffix'] + label

                graph.add_node(event, prefix=prefix, suffix='')
                prefix = prefix + label
                print(event)
        variants = variants_filter.get_variants(log)

        #        print('Variants')
        #       for variant in variants:
        #          print(variants[variant])
        #         print(len(variants[variant]))
        #    print(variants.keys())
        filtered_keys = [key.replace(',', '') for key in variants.keys()]
        print(filtered_keys)

    def get_edit_distance(self) -> integer:
        # for x in filtered_keys:
        #     for y in filtered_keys:
        #         print(editdistance.eval(x, y))
        pass
