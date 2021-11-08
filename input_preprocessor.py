import re

from igraph import Clustering
from pm4py.objects.log.importer.xes import importer as xes_importer

from apply_im import write_data_from_original_log_with_imprecise_labels, apply_im_with_noise_and_export, \
    apply_im_without_noise_and_export
from goldenstandardmodel import GoldenStandardModel
from input_data import InputData
from pipeline_helpers_shared import get_xixi_metrics, get_community_similarity
from pipeline_runner_single_layer_networkx import get_imprecise_labels
from pipeline_variant import remove_pipeline_variant_from_string, PipelineVariant
from pm4py.algo.filtering.log.variants import variants_filter


class InputPreprocessor:
    def __init__(self, input_data: InputData):
        self.input_data: InputData = input_data

    def preprocess_input(self):
        with open(f'./outputs/{self.input_data.input_name}.txt', 'a') as outfile:
            original_log = self.input_data.original_log

            xixi_precision = 0
            ground_truth_precision = 0
            labels_to_split = []
            ground_truth_model = None
            xixi_clustering = None

            if not self.input_data.labels_to_split:
                labels_to_split = get_imprecise_labels(original_log)
                ground_truth_model = GoldenStandardModel(self.input_data.input_name, '', self.input_data.log_path,
                                                         labels_to_split)
                ground_truth_precision = ground_truth_model.evaluate_golden_standard_model()
                ground_net = ground_truth_model.net
                ground_im = ground_truth_model.im
                ground_fm = ground_truth_model.fm
                print('ground_truth_precision')
                print(ground_truth_precision)

                xixi_precision, xixi_clustering = get_xixi_metrics(self.input_data.input_name, self.input_data.log_path, labels_to_split,
                                                  ground_net, ground_im,
                                                  ground_fm)
                print('xixi_precision')
                print(xixi_precision)

                export_model_from_original_log_with_precise_labels(self.input_data.input_name, self.input_data.log_path,
                                                                   self.input_data.use_noise)

            print('getting f1_scores')
            y_f1_scores_unrefined = write_data_from_original_log_with_imprecise_labels(self.input_data.input_name,
                                                                                       original_log,
                                                                                       self.input_data.use_noise)
            print('After')
            original_labels = self.get_original_labels(labels_to_split)
            outfile.write('\n Original Labels:\n')
            outfile.write(f'{str(original_labels)}\n')

            ground_truth_clustering = self.get_ground_truth_clustering(original_labels, labels_to_split)
            outfile.write('\n Ground truth clustering clustering:\n')
            outfile.write(f'{str(ground_truth_clustering)}\n')

            xixi_ari = get_community_similarity(ground_truth_clustering, xixi_clustering)
            outfile.write('\n Xixi Adjusted Rand Index:\n')
            outfile.write(f'{xixi_ari}\n')

            print('\n Xixi Adjusted Rand Index:\n')
            print(f'{xixi_ari}\n')

            self.input_data.xixi_precision = xixi_precision
            self.input_data.ground_truth_precision = ground_truth_precision
            self.input_data.y_f1_scores_unrefined = y_f1_scores_unrefined
            self.input_data.ground_truth_model = ground_truth_model
            self.input_data.labels_to_split = labels_to_split
            self.input_data.original_labels = original_labels
            self.input_data.ground_truth_clustering = ground_truth_clustering
            self.xixi_clustering = xixi_clustering
            self.xixi_ari = xixi_ari

    def get_original_labels(self, labels_to_split: list[str]) -> list:
        print('Getting original labels')
        original_labels = set()
        log = self.input_data.original_log

        variants = variants_filter.get_variants(log)

        for variant in variants:
            filtered_log = variants_filter.apply(log, [variant])
            for event in filtered_log[0]:
                if event['concept:name'] in labels_to_split:
                    original_labels.add(event['OrgLabel'])
        print('list(original_labels)')
        print(list(original_labels))
        return list(original_labels)

    def get_ground_truth_clustering(self, original_labels: list[str], labels_to_split: list[str]):
        log = self.input_data.original_log
        ground_truth_clustering = []
        variants = variants_filter.get_variants(log)

        if self.input_data.pipeline_variant != PipelineVariant.EVENTS:
            for variant in variants:
                filtered_log = variants_filter.apply(log, [variant])
                for event in filtered_log[0]:
                    if event['concept:name'] in labels_to_split:
                        ground_truth_clustering.append(original_labels.index(event['OrgLabel']))
        else:
            for trace in log:
                for event in trace:
                    if event['concept:name'] in labels_to_split:
                        ground_truth_clustering.append(original_labels.index(event['OrgLabel']))
        print('Clustering(ground_truth_clustering)')
        print(Clustering(ground_truth_clustering))
        return Clustering(ground_truth_clustering)


def export_model_from_original_log_with_precise_labels(input_name, path, use_noise=True):
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write('\n Data from log without imprecise labels\n')
        original_input_name = remove_pipeline_variant_from_string(input_name)
        original_input_name = re.sub(r'.*/', '', original_input_name)

        pattern = original_input_name + r'.*'
        log_path = re.sub(pattern, f'{original_input_name}_Log.xes.gz', path)
        original_log = xes_importer.apply(log_path)
        if use_noise:
            apply_im_with_noise_and_export(input_name, 'original_log_precise_labels', original_log, original_log,
                                           outfile)
        apply_im_without_noise_and_export(input_name, 'original_log_precise_labels', original_log, original_log,
                                          outfile)