import os
import sys

from pipeline.pipeline_runner import run_pipeline_for_artificial_event_logs, run_pipeline_for_real_log

folder_index= 0
directory = '../data/imprInLoop_adaptive_OD'
#folder_index = int(sys.argv[1])
#directory = sys.argv[2]


def main() -> None:
    input_paths = []
    for folder_name in (os.listdir(directory)):
        input_paths.append((os.path.join(directory, folder_name, 'logs/'), folder_name))

    run_pipeline_for_artificial_event_logs([input_paths[folder_index]])

    run_pipeline_for_real_log(input_name='real_logs/bpi_challenge_2017_3_cases_01_noise',
                              log_path='./data/real_logs/bpi_challenge_2017_3_cases_per_variant_shortened_labels.xes.gz',
                              folder_name='bpi_challenge_2017_3_cases_01_noise_missing_configs')
    return


main()
