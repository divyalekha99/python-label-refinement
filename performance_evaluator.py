import json
import string
from typing import TextIO

from pm4py.algo.evaluation.replay_fitness import evaluator as replay_fitness_evaluator
from pm4py.algo.evaluation.precision import evaluator as precision_evaluator
from pm4py.algo.evaluation.generalization import evaluator as generalization_evaluator
from pm4py.algo.evaluation.simplicity import evaluator as simplicity_evaluator


class PerformanceEvaluator:
    def __init__(self, net, im, fm, log, outfile: TextIO, skip_fitness=False):
        self.net = net
        self.im = im
        self.fm = fm
        self.log = log
        self.outfile = outfile
        self.precision = 0
        self.fitness = 0
        self.generalization = 0
        self.simplicity = 0
        self.skip_fitness = skip_fitness

    def _write(self, log_entry: string) -> None:
        self.outfile.write(f'{log_entry}\n')

    def evaluate_performance(self) -> None:
        self.get_fitness()
        self.get_precision()
        self.get_simplicity()
        self.get_generalization()

    def get_fitness(self):
        alignment_fitness = replay_fitness_evaluator.apply(self.log, self.net, self.im, self.fm,
                                                           variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED)
        self._write('alignment_fitness')
        self._write(json.dumps(alignment_fitness))
        self.fitness = alignment_fitness['averageFitness']

        return alignment_fitness

    def get_precision(self) -> float:
        precision = precision_evaluator.apply(self.log, self.net, self.im, self.fm,
                                              variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)

        self.precision = precision
        self._write('precision')
        self._write(json.dumps(precision))
        return precision

    def get_generalization(self) -> float:
        generalization = generalization_evaluator.apply(self.log, self.net, self.im, self.fm)
        self._write('generalization')
        self._write(json.dumps(generalization))
        self.generalization = generalization
        return generalization

    def get_simplicity(self):
        simplicity = simplicity_evaluator.apply(self.net)
        self.simplicity = simplicity
        self._write('simplicity')
        self._write(json.dumps(simplicity))
        return simplicity
