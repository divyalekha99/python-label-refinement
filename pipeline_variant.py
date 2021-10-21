import re
from enum import Enum


def remove_pipeline_variant_from_string(input_string: str):
    pattern = rf'\_({PipelineVariant.EVENTS}|{PipelineVariant.EVENTS_MULTI_GRAPH}|{PipelineVariant.VARIANTS}|{PipelineVariant.VARIANTS_MULTI_GRAPH})(_N_W)?'
    processed_input = re.sub(pattern, '', input_string)
    return processed_input


class PipelineVariant(Enum):
    EVENTS = 'EVENTS'
    EVENTS_MULTI_GRAPH = 'EVENTS_MULTI_GRAPH'
    VARIANTS = 'VARIANTS'
    VARIANTS_MULTI_GRAPH = 'VARIANTS_MULTI_GRAPH'

    def __str__(self):
        return str(self.value)
