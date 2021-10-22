from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from file_writer_helper import write_exception
from goldenstandardmodel import export_models_and_pngs
from performance_evaluator import PerformanceEvaluator
from post_processor import PostProcessor


def apply_im_without_noise_and_export(input_name, suffix, split_log, original_log, outfile, labels_to_original={},
                                      short_labels_to_original_labels={}):
    outfile.write(f'\n IM without noise threshold:\n')

    final_marking, initial_marking, final_net, precision = apply_im_without_noise(labels_to_original,
                                                                                  split_log,
                                                                                  original_log,
                                                                                  outfile,
                                                                                  short_labels_to_original_labels)
    tree = inductive_miner.apply_tree(split_log)

    export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_name, suffix)
    return precision


def apply_im_without_noise(labels_to_original, split_log, original_log, outfile, short_labels_to_original_labels={}):
    net, initial_marking, final_marking = inductive_miner.apply(split_log)
    post_processor = PostProcessor(labels_to_original, short_labels_to_original_labels)
    final_net = post_processor.post_process_petri_net(net)

    performance_evaluator = PerformanceEvaluator(final_net,
                                                 initial_marking,
                                                 final_marking,
                                                 original_log,
                                                 outfile,
                                                 skip_fitness=True)
    performance_evaluator.evaluate_performance()

    final_net = post_processor.rename_short_labels_to_original_labels(final_net)
    return final_marking, initial_marking, final_net, performance_evaluator.precision


def apply_im_with_noise_and_export(input_name, suffix, split_log, original_log, outfile, labels_to_original={},
                                   short_labels_to_original_labels={}):
    f1_scores = []
    for noise_threshold in [0, 0.1, 0.2, 0.3, 0.4]:
        outfile.write(f'\nnoise_threshold: {noise_threshold}\n')

        try:
            net, initial_marking, final_marking = inductive_miner.apply(split_log,
                                                                        variant=inductive_miner.Variants.IMf,
                                                                        parameters={
                                                                            inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})
        except Exception as e:
            write_exception(e, outfile)
            continue

        post_processor = PostProcessor(labels_to_original, short_labels_to_original_labels)
        final_net = post_processor.post_process_petri_net(net)

        performance_evaluator = PerformanceEvaluator(final_net, initial_marking, final_marking, original_log,
                                                     outfile)

        performance_evaluator.evaluate_performance()

        f1_score = get_f1_score(performance_evaluator.precision, performance_evaluator.fitness)
        f1_scores.append(f1_score)
        tree = inductive_miner.apply_tree(original_log,
                                          variant=inductive_miner.Variants.IMf,
                                          parameters={
                                              inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})
        export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_name, suffix)
    return f1_scores


def get_f1_score(precision, recall):
    print(recall)
    print(precision)
    print(2 * (precision * recall) / (precision + recall))
    return 2 * (precision * recall) / (precision + recall)


def write_data_from_original_log_with_imprecise_labels(input_name, original_log, use_noise=True):
    print(f'./outputs/{input_name}.txt')
    with open(f'./outputs/{input_name}.txt', 'a') as outfile:
        outfile.write('\nOriginal Data Performance:\n')
        f1_scores = apply_im_with_noise_and_export(input_name, 'original_log_imprecise_labels', original_log,
                                                   original_log,
                                                   outfile) if use_noise else []
        apply_im_without_noise_and_export(input_name, 'original_log_imprecise_labels', original_log, original_log,
                                          outfile)
    return f1_scores
