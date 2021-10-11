from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

from performance_evaluator import PerformanceEvaluator
from pipeline_runner_single_layer_networkx import save_models_as_png
from post_processor import PostProcessor


def apply_im_with_noise_and_export(input_name, suffix, original_log, outfile):
    for noise_threshold in [0, 0.1, 0.2, 0.3]:
        outfile.write(f'\nnoise_threshold: {noise_threshold}\n')

        original_net, initial_marking, final_marking = inductive_miner.apply(original_log,
                                                                             variant=inductive_miner.Variants.IMf,
                                                                             parameters={
                                                                                 inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})

        performance_evaluator = PerformanceEvaluator(original_net, initial_marking, final_marking, original_log,
                                                     outfile)

        performance_evaluator.evaluate_performance()
        # original_tree = inductive_miner.apply_tree(original_log,
        #                                            variant=inductive_miner.Variants.IMf,
        #                                            parameters={
        #                                                inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})
        # pnml_exporter.apply(original_net, initial_marking,
        #                     f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_{noise_threshold}_{suffix}.pnml',
        #                     final_marking=final_marking)
        # save_models_as_png(f'{input_name}_{noise_threshold}_{suffix}',
        #                    final_marking,
        #                    initial_marking,
        #                    original_net,
        #                    original_tree)


def apply_im_without_noise_and_export(input_name, suffix, original_log, outfile):
    outfile.write(f'\n IM without noise threshold:\n')

    original_net, initial_marking, final_marking = inductive_miner.apply(original_log)

    performance_evaluator = PerformanceEvaluator(original_net, initial_marking, final_marking, original_log,
                                                 outfile)

    performance_evaluator.evaluate_performance()
    original_tree = inductive_miner.apply_tree(original_log)
    pnml_exporter.apply(original_net, initial_marking,
                        f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_no_noise_{suffix}.pnml',
                        final_marking=final_marking)
    save_models_as_png(f'{input_name}_no_noise_{suffix}',
                       final_marking,
                       initial_marking,
                       original_net,
                       original_tree)
    return performance_evaluator.precision


def apply_im_with_noise_and_export_post_process(input_name, suffix, original_log, outfile, labels_to_original):
    for noise_threshold in [0, 0.1, 0.2, 0.3]:
        outfile.write(f'\nnoise_threshold: {noise_threshold}\n')

        net, initial_marking, final_marking = inductive_miner.apply(original_log,
                                                                    variant=inductive_miner.Variants.IMf,
                                                                    parameters={
                                                                        inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})

        post_processor = PostProcessor(labels_to_original)
        final_net = post_processor.post_process_petri_net(net)

        performance_evaluator = PerformanceEvaluator(final_net, initial_marking, final_marking, original_log,
                                                     outfile)

        performance_evaluator.evaluate_performance()
        # tree = inductive_miner.apply_tree(original_log,
        #                                   variant=inductive_miner.Variants.IMf,
        #                                   parameters={
        #                                       inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: noise_threshold})
        # pnml_exporter.apply(final_net, initial_marking,
        #                     f'/home/jonas/repositories/pm-label-splitting/outputs/{input_name}_{noise_threshold}_{suffix}.pnml',
        #                     final_marking=final_marking)
        # save_models_as_png(f'{input_name}_{noise_threshold}_{suffix}',
        #                    final_marking,
        #                    initial_marking,
        #                    final_net,
        #                    tree)