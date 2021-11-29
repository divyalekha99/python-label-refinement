from enum import Enum
from typing import Set

import editdistance


class DistanceVariant(Enum):
    EDIT_DISTANCE = 1
    SET_DISTANCE = 2
    MULTISET_DISTANCE = 3


class DistanceCalculator:
    def __init__(self, window_size: int = 3, use_combined_context=False):
        self.window_size = window_size
        self.use_combined_context = use_combined_context

    def get_edit_distance(self, event_a, event_b) -> float:
        if not self.use_combined_context:
            prefix_distance = editdistance.eval(
                event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):],
                event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):])
            # self._write(prefix_distance)
            suffix_distance = editdistance.eval(event_a['suffix'][:min(self.window_size, len(event_a['suffix'])) - 1],
                                                event_b['suffix'][:min(self.window_size, len(event_b['suffix'])) - 1])
            return prefix_distance * 0.5 + suffix_distance * 0.5
        # self._write(suffix_distance)
        else:
            return editdistance.eval(
                event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):] + event_a['suffix'][
                                                                                           :min(self.window_size, len(
                                                                                               event_a['suffix'])) - 1],
                event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):] + event_b['suffix'][
                                                                                           :min(self.window_size, len(
                                                                                               event_b['suffix'])) - 1])

    def get_set_distance(self, event_a, event_b) -> float:
        prefix_a = set(event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):])
        prefix_b = set(event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):])
        suffix_a = set(event_a['suffix'][:min(self.window_size, len(event_a['suffix'])) - 1])
        suffix_b = set(event_b['suffix'][:min(self.window_size, len(event_b['suffix'])) - 1])
        if not self.use_combined_context:
            prefix_distance = _get_set_distance_for_strings(prefix_a, prefix_b)
            suffix_distance = _get_set_distance_for_strings(suffix_a, suffix_b)

            return prefix_distance * 0.5 + suffix_distance * 0.5
        else:
            context_a = prefix_a | suffix_a
            context_b = prefix_b | suffix_b
            return _get_set_distance_for_strings(context_a, context_b)

    def get_multiset_distance(self, event_a, event_b) -> float:
        if not self.use_combined_context:
            prefix_distance = _get_multiset_distance_for_strings(
                event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):],
                event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):])
            suffix_distance = _get_multiset_distance_for_strings(
                event_a['suffix'][:min(self.window_size, len(event_a['suffix'])) - 1],
                event_b['suffix'][:min(self.window_size, len(event_b['suffix'])) - 1])

            return prefix_distance * 0.5 + suffix_distance * 0.5
        else:
            return _get_multiset_distance_for_strings(
                event_a['prefix'][(-1) * min(self.window_size, len(event_a['prefix'])):] + event_a['suffix'][
                                                                                           :min(self.window_size, len(
                                                                                               event_a['suffix'])) - 1],
                event_b['prefix'][(-1) * min(self.window_size, len(event_b['prefix'])):] + event_b['suffix'][
                                                                                           :min(self.window_size, len(
                                                                                               event_b['suffix'])) - 1])


def _get_set_distance_for_strings(string_a: Set[str], string_b: Set[str]) -> int:
    distance = 0
    if len(string_a) > len(string_b):
        long_sting = string_a
        short_string = string_b
    else:
        long_sting = string_b
        short_string = string_a
    for label in long_sting:
        if label not in short_string:
            distance += 1
    return distance


def _get_multiset_distance_for_strings(string_a, string_b) -> int:
    distance = 0
    if len(string_a) > len(string_b):
        long_sting = string_a
        short_string = string_b
    else:
        long_sting = string_b
        short_string = string_a

    for label in long_sting:
        if label not in short_string:
            distance += 1
        else:
            short_string = short_string.replace(label, '', 1)

    return distance
