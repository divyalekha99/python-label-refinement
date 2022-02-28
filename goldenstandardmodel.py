import re

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter

from performance_evaluator import PerformanceEvaluator
from pipeline_runner_single_layer_networkx import save_models_as_png
from pipeline_variant import remove_pipeline_variant_from_string


def export_models_and_pngs(final_marking, initial_marking, net, original_tree, input_name, suffix):
    pnml_exporter.apply(net, initial_marking,
                        f'./outputs/{suffix}.pnml', final_marking=final_marking)
    ptml_exporter.apply(original_tree, f'./outputs/{suffix}.ptml')
    return


def rename_transitions_to_original_label(imprecise_labels, net, labels_to_split):
    for transition in net.transitions:
        if transition.label is None:
            continue

        if transition.label not in imprecise_labels:
            transition.label = labels_to_split[0]


def get_input_identifier_from_variant_input_name(input_name: str):
    original_input_name = remove_pipeline_variant_from_string(input_name)
    original_input_name = re.sub(r'.*/', '', original_input_name)
    return original_input_name


def get_log_from_input_identifier(input_identifier, path):
    pattern = input_identifier + r'.*'
    log_path = re.sub(pattern, f'{input_identifier}_Log.xes.gz', path)
    log = xes_importer.apply(log_path)
    return log


class GoldenStandardModel:
    def __init__(self, input_name: str, original_input_name: str, path: str, labels_to_split):
        self._input_name = input_name
        self._path = path
        self._labels_to_split = labels_to_split
        self._input_identifier = original_input_name if original_input_name != '' \
            else get_input_identifier_from_variant_input_name(self._input_name)
        print('self._input_identifier')
        print(self._input_identifier)
        self._imprecise_log = xes_importer.apply(self._path)
        self.net = None
        self.im = None
        self.fm = None

    def evaluate_golden_standard_model(self):
        with open(f'./outputs/{self._input_name}.txt', 'a') as outfile:
            outfile.write('\n Performance of golden standard model:\n')
            log = get_log_from_input_identifier(self._input_identifier, path=self._path)

            imprecise_labels = attributes_filter.get_attribute_values(self._imprecise_log, 'concept:name')
            print(imprecise_labels)

            net, initial_marking, final_marking = inductive_miner.apply(log)

            rename_transitions_to_original_label(imprecise_labels, net, self._labels_to_split)

            self.net = net
            self.im = initial_marking
            self.fm = final_marking
            performance_evaluator = PerformanceEvaluator(net, initial_marking, final_marking, self._imprecise_log,
                                                         outfile, skip_fitness=True)
            performance_evaluator.evaluate_performance()

            original_tree = inductive_miner.apply_tree(log)
            export_models_and_pngs(final_marking, initial_marking, net, original_tree, self._input_name, 'no_noise_golden')

        return performance_evaluator.precision
