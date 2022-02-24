from dataclasses import dataclass, field
from typing import List, Iterable

from igraph import *

from goldenstandardmodel import GoldenStandardModel
from pipeline_variant import PipelineVariant
from pm4py.objects.log.importer.xes import importer as xes_importer


@dataclass
class InputData:
    log_path: str = ''
    original_input_name: str = ''
    folder_name: str = ''
    summary_file_name: str = ''
    pipeline_variant: PipelineVariant = PipelineVariant.VARIANTS
    use_frequency: bool = True
    use_noise: bool = False
    max_number_of_traces: int = 20000000
    input_name: str = ''
    xixi_precision: float = 0
    xixi_clustering: Clustering = None
    xixi_ari: float = 0
    ground_truth_model: GoldenStandardModel = None
    ground_truth_precision: float = 0
    ground_truth_clustering: Clustering = None
    use_combined_context: bool = False
    y_f1_scores_unrefined: object = field(default_factory=list)
    labels_to_split: Iterable[str] = field(default_factory=list)
    original_labels: Iterable[str] = field(default_factory=list)
    original_log: object = None
    original_log_precision: float = 0
    original_log_simplicity: float = 0
    original_log_generalization: float = 0
    original_log_fitness: float = 0
    concurrent_labels: Iterable[str] = field(default_factory=list)
