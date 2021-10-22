from pm4py.objects.petri_net.obj import PetriNet


class PostProcessor:
    def __init__(self, split_labels_to_original_labels: dict[str, str], short_labels_to_original_labels: dict[str, str]):
        self._split_labels_to_original_labels = split_labels_to_original_labels
        self._short_labels_to_original_labels = short_labels_to_original_labels

    def post_process_petri_net(self, net: PetriNet) -> PetriNet:
        for transition in net.transitions:
            if transition.label in self._split_labels_to_original_labels.keys():
                transition.label = self._split_labels_to_original_labels[transition.label]
        return net

    def rename_short_labels_to_original_labels(self, net):
        for transition in net.transitions:
            if transition.label in self._short_labels_to_original_labels.keys():
                transition.label = self._short_labels_to_original_labels[transition.label]
        return net
