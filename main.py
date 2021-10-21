import pandas as pd
import pm4py
from pm4py.objects.conversion.process_tree import converter
from pm4py.visualization.process_tree import visualizer as pt_visualizer

from pipeline_runner_multi_layer_igraph import run_pipeline_multi_layer_igraph


def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')
    num_events = len(event_log)
    num_cases = len(event_log.case_id.unique())
    print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))


def main() -> None:
    # run_pipeline_single_layer_networkx()
    run_pipeline_multi_layer_igraph()

    # bpmn_graph = pm4py.read_bpmn(f'/home/jonas/repositories/pm-label-splitting/bpmn_files/loop_example_th_0.bpmn')
    # log_generator = LogGenerator()
    # log = log_generator.get_log_from_bpmn(bpmn_graph)
    #
    # variants = variants_filter.get_variants(log)
    # print(variants.keys())
    #
    # for variant in variants:
    #     print(variant)
    #     print(variants[variant])
    #     print(len(variants[variant]))
    #     filtered_log1 = variants_filter.apply(log, [variant])
    #     for i in variant:
    #         print(i)
    #
    #     for trace in filtered_log1:
    #         for event in trace:
    #             event['Teeeeeeeeeeessssssst'] = 'Foo'
    # print('log')
    # print(log)

    # run_pipeline_single_layer_networkx()


def export_bpmn_model(log):
    tree = pm4py.discover_process_tree_inductive(log)
    bpmn_graph = converter.apply(tree, variant=converter.Variants.TO_BPMN)
    pm4py.write_bpmn(bpmn_graph, '/home/jonas/repositories/pm-label-splitting/test_files/test.bpmn', enable_layout=True)
    gviz = pt_visualizer.apply(tree)
    pt_visualizer.view(gviz)


main()
