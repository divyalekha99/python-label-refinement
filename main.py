import os
import sys
import graphviz
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'pm-label-splitting')))


from pipeline.pipeline_runner import run_pipeline_for_artificial_event_logs, run_pipeline_for_real_log
from pathlib import Path



folder_index = int(sys.argv[1])
directory = sys.argv[2]



def main() -> None:



    input_paths = []
    print(f"folder name:{folder_index}")
    print(f"directory name:{directory}")
    print(f"current working directory:{os.getcwd()}")
    for folder_name in (os.listdir(directory)):
        input_paths.append((os.path.join(directory, folder_name, 'logs/'), folder_name))




    # Manually add the Graphviz bin directory to the PATH (adjust the path as per your installation)
    # os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

    
    # run_pipeline_for_artificial_event_logs([input_paths[folder_index_position]])

    run_pipeline_for_real_log(input_name='BPI',
                              log_path="/Users/divyalekhas/Documents/Masters/replication_new/data/logs/Road_Traffic_Fine_Management_Process_shortened_labels.xes",
                              folder_name='outputs')
    

    return

main()
