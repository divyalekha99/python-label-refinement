import csv
import datetime
import os
from datetime import datetime
from pathlib import Path

from pipeline.pipeline_variant import PipelineVariant


def write_summary_file_with_parameters(best_configs, best_score, best_precision, name, summary_file_name):
    with open(f'./outputs/best_results/With_Parameters_{summary_file_name}', 'a') as outfile:
        outfile.write(get_result_header(name))
        outfile.write(f'\nBest found configs for {name}:')
        for config in best_configs:
            outfile.write(config)
        outfile.write('Score:\n')
        outfile.write(str(best_score))
        outfile.write('\nPrecision of best_score model :\n')
        outfile.write(str(best_precision))


def setup_result_folder(folder_name: str, pipeline_variant: PipelineVariant):
    if not os.path.exists('../../outputs/best_results'):
        os.makedirs('../../outputs/best_results')

    header = [
        'Name', 'max_number_of_traces', 'labels_to_split', 'original labels', 'original_precision',
        'original_simplicity',
        'original_generalization', 'original_fitness', 'Xixi number of Clusters found', 'Xixi Precision', 'Xixi ARI',
        'use_combined_context', 'use_frequency', 'window_size', 'distance_metric', 'threshold',
        'Number of Clusters found',
        'Precision Align', 'ARI', 'Simplicity', 'Generalization', 'Fitness', 'Runtime']

    Path(f'./outputs/{folder_name}').mkdir(parents=True, exist_ok=True)

    csv_file_path = Path(f'./results/{folder_name}_{pipeline_variant}_NEW.csv')
    if csv_file_path.is_file():
        print(csv_file_path)
        print('Warning: File already existis exiting')
        return

    with open(f'./results/{folder_name}_{pipeline_variant}_NEW.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)


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


def get_result_header(name):
    return '''

-------------------------------------------------------
Results for {name} from {date}
-------------------------------------------------------

'''.format(date=datetime.now(), name=name)


def write_summary_file(best_score, best_precision, golden_standard_precision, name, summary_file_name, xixi_precision, xixi_ari):
    with open(f'./outputs/best_results/{summary_file_name}', 'a') as outfile:
        outfile.write(f'\n\nBest score found for {name}:\n')
        outfile.write(f'{str(best_score)}\n')
        outfile.write(f'Precision of best_score model found for {name}:\n')
        outfile.write(f'{str(best_precision)}\n')
        if xixi_precision != 0:
            outfile.write(f'Precision found by Xixi for {name}:\n')
            outfile.write(f'{str(xixi_precision)}\n')
            outfile.write(f'Adjusted Rand Index from Xixi for {name}:\n')
            outfile.write(f'{str(xixi_ari)}\n')
        if golden_standard_precision != 0:
            outfile.write(f'Golden_standard_precision for {name}:\n')
            outfile.write(f'{str(golden_standard_precision)}\n')


def write_exception(e, outfile):
    print('----------------Exception occurred------------------------')
    print(e)
    outfile.write(f'´\n----------------Exception occurred------------------------\n')
    outfile.write(f'{repr(e)}\n')
