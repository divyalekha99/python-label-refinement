import json
import re
import sys
import string
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def main(args) -> None:
    print(args)
    log_path = args[1]
    log = xes_importer.apply(log_path)
    label_mapping = {}
    i = 0

    for trace in log:
        for event in trace:
            label = event['concept:name']
            if label not in label_mapping:
                label_mapping[label] = string.printable[i]
                print(label)
                i += 1
            event['original_label'] = label
            event['concept:name'] = label_mapping[label]
            # print(label_mapping[label])

    pattern = r'/(.*)\.xes'
    match = re.match(pattern, log_path)

    new_log_path = re.sub(match.group(1), f'{match.group(1)}_shortened_labels', log_path)
    print(log)
    print(json.dumps(label_mapping))
    xes_exporter.apply(log, new_log_path)


main(sys.argv)
