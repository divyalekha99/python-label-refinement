import os
import sys

from pipeline.pipeline_runner import run_pipeline_for_artificial_event_logs, run_pipeline_for_real_log

folder_index = int(sys.argv[1])
directory = sys.argv[2]


def main() -> None:
    input_paths = []
    for folder_name in (os.listdir(directory)):
        input_paths.append((os.path.join(directory, folder_name, 'logs/'), folder_name))

    run_pipeline_for_artificial_event_logs([input_paths[folder_index]])

    run_pipeline_for_real_log(input_name='name_to_identify_the_log_with',
                              log_path='path_to_log',
                              folder_name='folder_to_associate_with_the_log_for_the_outputs')
    return


main()
