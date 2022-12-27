# (Third functionality / step: Compute Performance)
# Input: Event Log
# Output: Performance results
# Mine model and check quality of the model
#
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
        # Models expected to have fitness 1 (Inductive miner)
        # self._write(log)
        # if self.skip_fitness:
        #     print('Fitness skipped because of IM without noise')
        #     self.fitness = 1
        #     self._write('Fitness skipped, assumed to be 1 because of IM')
        #     return 1
        token_fitness = replay_fitness_evaluator.apply(self.log, self.net, self.im, self.fm, variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
        self._write('token_fitness')
        self._write(json.dumps(token_fitness))


        # alignment_fitness = replay_fitness_evaluator.apply(self.log, self.net, self.im, self.fm,
        #                                                    variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED)
        # self._write('alignment_fitness')
        # self._write(json.dumps(alignment_fitness))
        # self.fitness = token_fitness['averageFitness']
        # self.fitness = token_fitness['average_trace_fitness']
        self.fitness = token_fitness['average_trace_fitness']

        return self.fitness

    def get_precision(self) -> float:
        # Slower, but "more precise" version
        # precision = precision_evaluator.apply(self.log, self.net, self.im, self.fm,
        #                                       variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)

        precision = precision_evaluator.apply(self.log, self.net, self.im, self.fm,
                                              variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
        self.precision = precision
        self._write('precision')
        self._write(json.dumps(precision))
        return precision

    def get_generalization(self) -> float:
        # generalization = generalization_evaluator.apply(self.log, self.net, self.im, self.fm)
        # self._write('generalization')
        # self._write(json.dumps(generalization))
        self._write('Generalization skipped')
        self.generalization = 99999
        return 99999

    def get_simplicity(self):
        # simplicity = simplicity_evaluator.apply(self.net)
        self.simplicity = 99999
        self._write('simplicity skipped')
        # self._write(json.dumps(simplicity))
        return 99999
