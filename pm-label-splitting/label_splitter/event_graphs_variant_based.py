import igraph
from pm4py.algo.filtering.log.variants import variants_filter


class EventGraphsVariantBased:
    """
    Event graph where each node represents one event of a variant
    """
    def __init__(self, event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count):
        self.event_graphs = event_graphs
        self.short_label_to_original_label = short_label_to_original_label
        self.label_and_id_to_event = label_and_id_to_event
        self.variants_to_count = variants_to_count


def get_event_graphs_from_event_log(log, labels_to_split):
    """
    Extracts the event graphs for the labels to split from the event log

    :return: Generated event graph with variant compression, i.e., nodes per variant instead of per event
    """
    print('Variants based approach')
    variants = variants_filter.get_variants(log)
    event_graphs = {}
    short_label_to_original_label = {}
    label_and_id_to_event = {}
    variants_to_count = {}
    variant_to_sample_case = {}

    for case in log:
        variant = ''
        for e in case:
            variant = f"{variant},{e['concept:name']}"
        if variant not in variant_to_sample_case:
            variant_to_sample_case[variant[1:]] = case
        for e in case:
            e['variant_raw'] = variant.replace(',', '')
    print('Variants:', variants)

    for variant in variants:
        prefix = ''
        processed_events = []
        occurrence_counters = {}
        print('Variant:', variant)
        # print('Variant to sample case:', variant_to_sample_case)
        # for event in variant_to_sample_case[str(variant)]:
        # print('Variant:', variant)
        variant_str = ','.join(variant)  # Convert the variant tuple to a string
    
        print('Variant:', variant_str)  # Print the variant string
        
        if variant_str in variant_to_sample_case:  # Check if the string version of the variant is in the sample cases
            print(f"Variant {variant_str} found in sample cases.")
        else:
            print(f"Variant {variant_str} not found in sample cases.")

        for event in variant_to_sample_case.get(variant_str, []):
            print("GOing in lable")
            label = event['concept:name']
            print('Label:', label)
            if 'original_label' in event.keys():
                short_label_to_original_label[label] = event['original_label']

            if label not in list(event_graphs.keys()) and label in labels_to_split:
                event_graphs[label] = igraph.Graph()
                label_and_id_to_event[label] = []

            for preceding_event in processed_events:
                preceding_event['suffix'] = preceding_event['suffix'] + label

            if label not in occurrence_counters:
                occurrence_counters[label] = 0
            else:
                occurrence_counters[label] += 1

            event['prefix'] = prefix
            event['suffix'] = ''
            event['label'] = label
            event['variant'] = label + '_' + event['variant_raw'] + f'_{occurrence_counters[label]}'
            variants_to_count[event['variant']] = len(variants[variant])
            processed_events.append(event)
            prefix = prefix + label
        for event in processed_events:
            label = event['concept:name']
            print('vanten', label, labels_to_split)
            if label in labels_to_split:
                label_and_id_to_event[label].append(event)
                print('Ebba')
                event_graphs[label].add_vertices(1)

        print("Event graphs:", event_graphs)

    return EventGraphsVariantBased(event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count)