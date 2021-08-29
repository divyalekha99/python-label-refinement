from pm4py.objects.petri_net.obj import PetriNet


class PostProcessor:
    def __init__(self):
        pass

    def post_process_petri_net(self, net: PetriNet) -> PetriNet:
        for transition in net.transitions:
            if transition.label == 'D_0' or transition.label == 'D_1':
                transition.label = 'D'
        return net