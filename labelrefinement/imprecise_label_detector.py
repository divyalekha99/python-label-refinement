import os
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pm4py
def oracle_detection(log):
    imprecise_labels = set()
    original_labels = set()
    for trace in log:
        for event in trace:
            if event["OrgLabel"] != event["concept:name"]:
                original_labels.add(event["OrgLabel"])
                imprecise_labels.add(event["concept:name"])

    original_labels = list(original_labels)
    imprecise_labels = list(imprecise_labels)
    original_labels.append(imprecise_labels[0])
    return original_labels, imprecise_labels

def label_in_flower_detector(log):
    #todo
    '''
    tree = inductive_miner.apply_tree(log)
    for node in tree.children:
        print(node)
    print("label: ", tree.label)
    bottomup =pm4py.objects.process_tree.bottomup.get_bottomup_nodes(tree)
    print("bottomup: ", bottomup)
    for b in bottomup:
        b.parent
    return 0'''
    return [], []
