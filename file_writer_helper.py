from datetime import datetime


def run_start_string():
    return '''



----------------------------------------------------------------------------------------------
Output from {date}
----------------------------------------------------------------------------------------------


                '''.format(date=datetime.now())


def get_config_string(clustering_variant, distance_variant, labels_to_split, number_of_traces, original_log_path,
                      threshold, window_size, use_frequency=True):
    return '''

Parameters of this run:

Window size: {window_size}
Threshold for edges: {threshold}
Split candidates: {labels_to_split}
Max number of traces: {number_of_traces}
Method for distance calculation: {distance_variant}
Method for finding clusters: {clustering_variant}
Original log location: {original_log_path}
Use frequency: {use_frequency}

'''.format(threshold=threshold,
           window_size=window_size,
           labels_to_split=''.join(labels_to_split),
           number_of_traces=number_of_traces,
           distance_variant=distance_variant,
           clustering_variant=clustering_variant,
           original_log_path=original_log_path,
           use_frequency=use_frequency)
