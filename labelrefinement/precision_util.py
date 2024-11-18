from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter, variants
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import pm4py
from time import time
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator


def get_precision(ref_log, event_log, imprecise_labels, graph_parameters):
    # for case_id, case in enumerate(ref_log):
    #    for event_id, event in enumerate(case):
    #        print(event)
    #        print(event_log[case_id][event_id])
    #        print(".")
    #    print("---------")
    # print("---------------------------------------------------------------------------------")

    # for case in event_log:
    #    for event in case:
    #        print(event)
    #    print("---------")

    # print("get_prec")
    # print("a")
    tree = inductive_miner.apply(ref_log, parameters={"ACTIVITY_KEY": graph_parameters["ACTIVITY_KEY"]})
    net, initial_marking, final_marking = converter.apply(tree, variant=converter.Variants.TO_PETRI_NET)
    # gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    # pn_visualizer.view(gviz)

    # print("b")
    for transition in net.transitions:
        if transition.label != None and transition.label.split("_X_", 1)[0] in imprecise_labels:
            print("check", transition.label)
            transition.label = imprecise_labels[0]
    # print("c")
    # gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    # pn_visualizer.view(gviz)

    # prec = precision_evaluator.apply(event_log, net, initial_marking, final_marking, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
    time1 = time()
    # print("moin1: ")
    prec = precision_evaluator.apply(event_log, net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
    generalization = generalization_evaluator.apply(event_log, net, initial_marking, final_marking)
    simplicity = simplicity_evaluator.apply(net)

    time2 = time()
    print("precision time: ", time2 - time1)
    # prec = pm4py.evaluation.precision.versions.align_etconformance.apply(event_log, net, initial_marking, final_marking)
    # print("d")
    return prec, simplicity, generalization


def get_number_of_different_original_labels(event_log):
    original_labels = []
    for trace in event_log:
        for event in trace:
            orig_label = event["OrgLabel"]
            if orig_label not in original_labels:
                original_labels.append(orig_label)

    return len(original_labels)


def get_precision_of_original_model(net, initial_marking, final_marking, event_log, imprecise_labels, original_labels,
                                    graph_parameters):
    # print("get_prec_of_original_model")
    print(original_labels)
    print(imprecise_labels)
    for transition in net.transitions:
        print(transition.label)
        if transition.label != None and transition.label in original_labels:
            transition.label = imprecise_labels[0]  # todo rework so that original_labels becomes dictionary
            print('after swap')
            print(transition.label)

    generalization = generalization_evaluator.apply(event_log, net, initial_marking, final_marking)
    simplicity = simplicity_evaluator.apply(net)
    prec = precision_evaluator.apply(event_log, net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
    return prec, simplicity, generalization


def get_precision_of_precice_log(original_event_log, event_log, imprecise_labels, original_labels, graph_parameters):
    # print("get_prec_of_precise_log")
    # net, initial_marking, final_marking = inductive_miner.apply(original_event_log, parameters={
    #     inductive_miner.Variants.IMf.value.Parameters.ACTIVITY_KEY: graph_parameters["ACTIVITY_KEY"]})
    tree = inductive_miner.apply(original_event_log, parameters={"ACTIVITY_KEY": graph_parameters["ACTIVITY_KEY"]})
    net, initial_marking, final_marking = converter.apply(tree, variant=converter.Variants.TO_PETRI_NET)
    
    
    
    # net, initial_marking, final_marking = converter.apply(tree, variant=converter.Variants.TO_PETRI_NET)
    
    for transition in net.transitions:
        if transition.label != None and transition.label in original_labels:
            transition.label = imprecise_labels[0]  # todo rework so that original_labels becomes dictionary

    prec = precision_evaluator.apply(event_log, net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)

    generalization = generalization_evaluator.apply(event_log, net, initial_marking, final_marking)
    simplicity = simplicity_evaluator.apply(net)
    return prec,  simplicity, generalization
