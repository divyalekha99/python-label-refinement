

class PostProcessor:
    def __init__(self, split_labels_to_original_labels, short_labels_to_original_labels):
        self._split_labels_to_original_labels = split_labels_to_original_labels
        self._short_labels_to_original_labels = short_labels_to_original_labels

    def post_process_petri_net(self, net):
        for transition in net.transitions:
            if transition.label is not None and transition.label[0] in self._split_labels_to_original_labels.values():
                transition.label = transition.label[0]
        return net

    def rename_short_labels_to_original_labels(self, net):
        for transition in net.transitions:
            if transition.label in self._short_labels_to_original_labels.keys():
                transition.label = self._short_labels_to_original_labels[transition.label]
        return net
