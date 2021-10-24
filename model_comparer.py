import copy
from typing import TextIO

from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog, Event
from pm4py.objects.petri_net.data_petri_nets import semantics
import pm4py.objects.petri_net.data_petri_nets
from pm4py.objects.petri_net.data_petri_nets.data_marking import DataMarking
from pm4py.objects.petri_net.obj import PetriNet, Marking


class ModelComparer:
    def __init__(self, golden_standard: PetriNet, im_a: Marking, fm_a: Marking, net_b: PetriNet, im_b: Marking,
                 fm_b: Marking, log: EventLog, outfile: TextIO, precision: float):
        self.net_a = golden_standard
        self.im_a = DataMarking(im_a)
        self.fm_a = fm_a
        self.net_b = net_b
        self.im_b = DataMarking(im_b)
        self.fm_b = fm_b
        self.log = log
        self.outfile = outfile
        self.precision = precision
        self.fitness = 0

    def get_enabled_transitions(self, pn, m, e):
        enabled = set()
        transition_to_marking = {}

        for t in pn.transitions:
            #
            # print(t)
            # print(m)
            # print(e)
            if semantics.is_enabled(t, pn, m, e):
                if t.label is None:
                    # print('Silent transition')
                    m_s = semantics.execute(t, pn, m, e)
                    # print('m_s')
                    # print(m_s)
                    if t in transition_to_marking.keys():
                        # print('################## Continued ##################')
                        continue

                    enabled_s, transition_to_marking_s = self.get_enabled_transitions(pn, m_s, e)
                    enabled |= enabled_s
                    transition_to_marking |= transition_to_marking_s
                else:
                    transition_to_marking[t] = m
                    enabled.add(t)
        # print('enabled')
        # print(enabled)
        return enabled, transition_to_marking

    def get_overlap(self, enabled_a, enabled_b):
        labels_a = set()
        for t in enabled_a:
            labels_a.add(t.label)

        labels_b = set()
        for t in enabled_b:
            labels_b.add(t.label)
        #
        # print('labels_a')
        # print(labels_a)
        # print('labels_b')
        # print(labels_b)

        overlap = labels_a.intersection(labels_b)
        return overlap

    def compare_models(self):
        precision = 0
        recall = 0
        log_size = 0
        variants = variants_filter.get_variants(self.log)
        for variant in variants:
            filtered_log = variants_filter.apply(self.log, [variant])
            variant_count = len(variants[variant])
            log_size += variant_count
            m_a = copy.copy(self.im_a)
            m_b = copy.copy(self.im_b)

            trace = [e for e in filtered_log[0]]
            # print('filtered_log[0]')
            # print(trace)
            # print('Length')
            # print(len(trace))

            precision_s, recall_s = self.get_behavioral_metrics(trace, m_a, m_b)
            precision += precision_s * variant_count / len(trace)
            recall += recall_s * variant_count / len(trace)
        return precision * 1 / log_size, recall * 1 / log_size

    def get_behavioral_metrics(self, trace: list[Event], m_a, m_b):
        # print('trace')
        # print(trace)
        # print('len(trace)')
        # print(len(trace))
        precision = 0
        recall = 0

        if len(trace) == 0:
            return 0, 0
        e = trace[0]

        # print('before')
        enabled_a, t_to_m_a = self.get_enabled_transitions(self.net_a, m_a, e)
        # print('after')
        enabled_b, t_to_m_b = self.get_enabled_transitions(self.net_b, m_b, e)
        overlap = self.get_overlap(enabled_a, enabled_b)

        # print('overlap test')
        # print(overlap)
        # print('enabled_b test')
        # print(enabled_b)
        # print('enabled_a test')
        # print(enabled_a)

        precision += len(overlap) / len(enabled_b) if len(enabled_b) > 0 else 0
        recall += len(overlap) / len(enabled_a) if len(enabled_a) > 0 else 0

        # print('Calculated precision')
        # print(precision)

        valid_a = [t for t in enabled_a if t.label == e['concept:name']]
        valid_b = [t for t in enabled_b if t.label == e['concept:name']]

        # for t in enabled_a:
        #     print('##############################################')
        #     print(t.label)
        #     print(e['concept:name'])
        #     print('##############################################')
        #
        # print('valid_a')
        # print(valid_a)
        # print('valid_b')
        # print(valid_b)

        for t_a in valid_a:
            for t_b in valid_b:
                n_m_a = semantics.execute(t_a, self.net_a, t_to_m_a[t_a], e)
                n_m_b = semantics.execute(t_b, self.net_b, t_to_m_b[t_b], e)
                n_precision, n_recall = self.get_behavioral_metrics(trace[1:], n_m_a, n_m_b)

                precision += 1 / (len(valid_a) * len(valid_b)) * n_precision
                recall += 1 / (len(valid_a) * len(valid_b)) * n_recall
                # print('precision')
                # print(precision)
                # print('recall')
                # print(recall)
        return precision, recall
