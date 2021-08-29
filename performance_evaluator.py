# (Third functionality / step: Compute Performance)
# Input: Event Log
# Output: Performance results
# Mine model and check quality of the model
#
from typing import Any

from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness_evaluator
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator


class PerformanceEvaluator:
    def __init__(self, net: PetriNet, im: Marking, fm: Marking, log: EventLog):
        self.net = net
        self.im = im
        self.fm = fm
        self.log = log

    def evaluate_performance(self) -> None:
        self.get_fitness()
        self.get_precision()
        self.get_simplicity()
        self.get_generalization()

    def get_fitness(self) -> dict[str, Any]:
        # print(log)
        # token_fitness = replay_fitness_evaluator.apply(log, net, im, fm, variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
        # print(token_fitness)
        alignment_fitness = replay_fitness_evaluator.apply(self.log, self.net, self.im, self.fm,
                                                           variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED)
        print('alignment_fitness')
        print(alignment_fitness)

        return alignment_fitness

    def get_precision(self) -> float:
        precision = precision_evaluator.apply(self.log, self.net, self.im, self.fm,
                                              variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
        print('precision')
        print(precision)
        return precision

    def get_generalization(self) -> float:
        generalization = generalization_evaluator.apply(self.log, self.net, self.im, self.fm)
        print('generalization')
        print(generalization)
        return generalization

    def get_simplicity(self):
        simplicity = simplicity_evaluator.apply(self.net)
        print('simplicity')
        print(simplicity)
        return simplicity
