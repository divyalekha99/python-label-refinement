import copy
import csv
import os
import time

from pathlib import Path

from pm4py.objects.log.importer.xes import importer as xes_importer

import clustering_variant
from apply_im import apply_im_with_noise_and_export, apply_im_without_noise
from distance_metrics import DistanceVariant
from file_writer_helper import get_config_string, write_summary_file, \
    write_summary_file_with_parameters, run_start_string
from goldenstandardmodel import export_models_and_pngs
from input_data import InputData
from input_preprocessor import InputPreprocessor
from label_splitter_event_based_igraph import LabelSplitter as LabelSplitterEventBased
from label_splitter_variant_based_igraph import LabelSplitter as LabelSplitterVariantBased, \
    get_event_graphs_from_event_log
from label_splitter_variant_multiplex import LabelSplitter as LabelSplitterVariantMultiplex
from pipeline_helpers_shared import get_tuples_for_folder, get_community_similarity, filter_duplicate_xor
from pipeline_variant import PipelineVariant
from plot_helpers import plot_noise_to_f1_score
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

# from pm4py.objects.petri_net.exporter import exporter as pnml_exporter


def run_pipeline_multi_layer_igraph(input_paths) -> None:

    if not os.path.exists('./outputs/best_results'):
        os.makedirs('./outputs/best_results')

    # {"Create Report": "0", "Attach Receipts": "1", "Write Supporting Motivation": "2", "Send Report": "3", "Receive Confirmation": "4", "Receive Revision Request": "5"}
    # apply_pipeline_to_folder([('real_logs/caise_23',
    #                            './real_logs/log_running_example_caise23_shortened_labels.xes')],
    #                          'paper.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"A_Create Application": "0", "A_Submitted": "1", "W_Handle leads": "2", "W_Complete application": "3",
    #  "A_Concept": "4", "A_Accepted": "5", "O_Create Offer": "6", "O_Created": "7", "O_Sent (mail and online)": "8",
    #  "W_Call after offers": "9", "A_Complete": "a", "W_Validate application": "b", "A_Validating": "c",
    #  "O_Returned": "d", "W_Call incomplete files": "e", "A_Incomplete": "f", "O_Accepted": "g", "A_Pending": "h",
    #  "A_Denied": "i", "O_Refused": "j", "O_Cancelled": "k", "A_Cancelled": "l", "O_Sent (online only)": "m",
    #  "W_Assess potential fraud": "n", "W_Personal Loan collection": "o", "W_Shortened completion ": "p"}

    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2017',
    #                            './real_logs/bpi_challenge_2017_shortened_labels.xes.gz')],
    #                          'bpi_challenge_2017',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['9'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"NEW": "0", "FIN": "1", "RELEASE": "2", "CODE OK": "3", "BILLED": "4", "DELETE": "5", "REOPEN": "6",
    #  "CHANGE DIAGN": "7", "STORNO": "8", "REJECT": "9", "CODE NOK": "a", "SET STATUS": "b", "CHANGE END": "c",
    #  "MANUAL": "d", "JOIN-PAT": "e", "CODE ERROR": "f", "ZDBC_BEHAN": "g", "EMPTY": "h"}
    # apply_pipeline_to_folder([('real_logs/hospital_billing_3',
    #                            './real_logs/hospital_billing_shortened_labels.xes.gz')],
    #                          'hospital_billing_3',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)
    #
    # apply_pipeline_to_folder([('real_logs/hospital_billing_1',
    #                            './real_logs/hospital_billing_shortened_labels.xes.gz')],
    #                          'hospital_billing_1',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)

    #{"Queued Awaiting Assignment": "0", "Accepted In Progress": "1", "Accepted Assigned": "2", "Completed Closed": "3", "Accepted Wait": "4", "Unmatched Unmatched": "5", "Completed Cancelled": "6"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2013_closed_problem',
    #                            './real_logs/bpi_challenge_2013_closed_problems_shortened_labels.xes.gz')],
    #                          'bpi_challenge_2013_closed_problem',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"Queued": "0", "Accepted": "1", "Completed": "2", "Unmatched": "3"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2013_without_life_cycle',
    #                            './real_logs/bpi_2013_challenge_without_lifecycle.xes.gz')],
    #                          'bpi_challenge_2013_without_lifecycle',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)


    # {"Confirmation of receipt": "0", "T02 Check confirmation of receipt": "1", "T03 Adjust confirmation of receipt": "2", "T06 Determine necessity of stop advice": "3", "T10 Determine necessity to stop indication": "4", "T04 Determine confirmation of receipt": "5", "T05 Print and send confirmation of receipt": "6", "T16 Report reasons to hold request": "7", "T17 Check report Y to stop indication": "8", "T19 Determine report Y to stop indication": "9", "T20 Print report Y to stop indication": "a", "T11 Create document X request unlicensed": "b", "T12 Check document X request unlicensed": "c", "T14 Determine document X request unlicensed": "d", "T15 Print document X request unlicensed": "e", "T07-1 Draft intern advice aspect 1": "f", "T08 Draft and send request for advice": "g", "T09-1 Process or receive external advice from party 1": "h", "T07-5 Draft intern advice aspect 5": "i", "T09-4 Process or receive external advice from party 4": "j", "T07-3 Draft intern advice hold for aspect 3": "k", "T07-4 Draft internal advice to hold for type 4": "l", "T07-2 Draft intern advice aspect 2": "m", "T13 Adjust document X request unlicensed": "n", "T09-3 Process or receive external advice from party 3": "o", "T18 Adjust report Y to stop indicition": "p", "T09-2 Process or receive external advice from party 2": "q"}
    # apply_pipeline_to_folder([('real_logs/environmental_permit',
    #                            './real_logs/environmental_permit_shortened_labels.xes.gz')],
    #                          'environmental_permit',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"A_SUBMITTED": "0", "A_PARTLYSUBMITTED": "1", "A_PREACCEPTED": "2", "W_Completeren aanvraag": "3", "A_ACCEPTED": "4", "O_SELECTED": "5", "A_FINALIZED": "6", "O_CREATED": "7", "O_SENT": "8", "W_Nabellen offertes": "9", "O_SENT_BACK": "a", "W_Valideren aanvraag": "b", "A_REGISTERED": "c", "A_APPROVED": "d", "O_ACCEPTED": "e", "A_ACTIVATED": "f", "O_CANCELLED": "g", "W_Wijzigen contractgegevens": "h", "A_DECLINED": "i", "A_CANCELLED": "j", "W_Afhandelen leads": "k", "O_DECLINED": "l", "W_Nabellen incomplete dossiers": "m", "W_Beoordelen fraude": "n"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2012',
    #                            './real_logs/bpi_challenge_2012_shortened_labels.xes.gz')],
    #                          'bpi_challenge_2012',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # apply_pipeline_to_folder([('real_logs/road_traffic_fines',
    #                            './real_logs/Road_Traffic_Fine_Management_Process_shortened_labels.xes.gz')],
    #                          'real_logs.txt',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['F'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"A_Create Application": "0", "A_Submitted": "1", "W_Handle leads": "2", "W_Complete application": "3", "A_Concept": "4", "A_Accepted": "5", "O_Create Offer": "6", "O_Created": "7", "O_Sent (mail and online)": "8", "W_Call after offers": "9", "A_Complete": "a", "W_Validate application": "b", "A_Validating": "c", "O_Returned": "d", "W_Call incomplete files": "e", "A_Incomplete": "f", "O_Accepted": "g", "A_Pending": "h", "A_Cancelled": "i", "O_Cancelled": "j", "A_Denied": "k", "O_Refused": "l", "O_Sent (online only)": "m", "W_Assess potential fraud": "n", "W_Shortened completion": "o"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2017_2_cases',
    #                                './real_logs/bpi_challenge_2017_2_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2017_2_cases',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split=['9'],
    #                             use_frequency=True,
    #                             use_noise=False)

    # {"A_SUBMITTED": "0", "A_PARTLYSUBMITTED": "1", "A_DECLINED": "2", "A_PREACCEPTED": "3", "W_Completeren aanvraag": "4", "A_CANCELLED": "5", "W_Afhandelen leads": "6", "A_ACCEPTED": "7", "O_SELECTED": "8", "A_FINALIZED": "9", "O_CREATED": "a", "O_SENT": "b", "W_Nabellen offertes": "c", "O_SENT_BACK": "d", "W_Valideren aanvraag": "e", "O_DECLINED": "f", "O_CANCELLED": "g", "O_ACCEPTED": "h", "A_ACTIVATED": "i", "A_APPROVED": "j", "A_REGISTERED": "k", "W_Beoordelen fraude": "l", "W_Nabellen incomplete dossiers": "m"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2012_2_cases',
    #                                './real_logs/bpi_challenge_2012_2_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2012_2_cases',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split = ['4'],
    #                             use_frequency = True,
    #                             use_noise=False)


    # {"SRM: Created": "0", "SRM: Complete": "1", "SRM: Awaiting Approval": "2", "SRM: Document Completed": "3", "SRM: In Transfer to Execution Syst.": "4", "SRM: Ordered": "5", "SRM: Change was Transmitted": "6", "Create Purchase Order Item": "7", "Vendor creates invoice": "8", "Record Goods Receipt": "9", "Record Invoice Receipt": "a", "Clear Invoice": "b", "Remove Payment Block": "c", "Record Service Entry Sheet": "d", "SRM: Transfer Failed (E.Sys.)": "e", "SRM: Deleted": "f", "Delete Purchase Order Item": "g", "Change Final Invoice Indicator": "h", "Receive Order Confirmation": "i", "Change Quantity": "j", "Change Price": "k", "Change Delivery Indicator": "l", "Vendor creates debit memo": "m", "Cancel Invoice Receipt": "n", "Cancel Subsequent Invoice": "o", "Reactivate Purchase Order Item": "p", "Update Order Confirmation": "q", "Block Purchase Order Item": "r", "Change Approval for Purchase Order": "s", "Create Purchase Requisition Item": "t", "Cancel Goods Receipt": "u", "Set Payment Block": "v", "Release Purchase Order": "w", "Change Storage Location": "x", "Record Subsequent Invoice": "y", "Change Currency": "z", "Release Purchase Requisition": "A"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2019_3_cases',
    #                            './real_logs/bpi_challenge_2019_3_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2019_3_cases',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split = ['9'],
    #                             use_frequency = True,
    #                             use_noise=False)

    # {"NEW": "0", "FIN": "1", "RELEASE": "2", "CODE OK": "3", "BILLED": "4", "DELETE": "5", "REOPEN": "6", "CHANGE DIAGN": "7", "STORNO": "8", "REJECT": "9", "CODE NOK": "a", "SET STATUS": "b", "CHANGE END": "c", "MANUAL": "d", "JOIN-PAT": "e", "CODE ERROR": "f", "EMPTY": "g"}
    # apply_pipeline_to_folder([('real_logs/hospital_billing_3_2_cases',
    #                            './real_logs/hospital_billing_2_cases_per_variant_shortened_labels.xes.gz')],
    #                          'hospital_billing_3_2_cases',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)
    #
    # apply_pipeline_to_folder([('real_logs/hospital_billing_1_2_cases',
    #                            './real_logs/hospital_billing_2_cases_per_variant_shortened_labels.xes.gz')],
    #                          'hospital_billing_1_2_cases',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"ER Registration": "0", "Leucocytes": "1", "CRP": "2", "LacticAcid": "3", "ER Triage": "4", "ER Sepsis Triage": "5", "IV Liquid": "6", "IV Antibiotics": "7", "Admission NC": "8", "Release A": "9", "Return ER": "a", "Admission IC": "b", "Release B": "c", "Release C": "d", "Release D": "e", "Release E": "f"}
    # apply_pipeline_to_folder([('real_logs/sepsis',
    #                            './real_logs/sepsis_shortened_labels.xes.gz')],
    #                          'sepsis',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"A_SUBMITTED": "0", "A_PARTLYSUBMITTED": "1", "A_DECLINED": "2", "A_PREACCEPTED": "3", "W_Completeren aanvraag": "4", "A_CANCELLED": "5", "W_Afhandelen leads": "6", "A_ACCEPTED": "7", "O_SELECTED": "8", "A_FINALIZED": "9", "O_CREATED": "a", "O_SENT": "b", "W_Nabellen offertes": "c", "O_SENT_BACK": "d", "W_Valideren aanvraag": "e", "O_DECLINED": "f", "O_CANCELLED": "g", "W_Beoordelen fraude": "h", "O_ACCEPTED": "i", "A_REGISTERED": "j", "A_ACTIVATED": "k", "A_APPROVED": "l", "W_Nabellen incomplete dossiers": "m"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2012_3_cases',
    #                                './real_logs/bpi_challenge_2012_3_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2012_3_cases',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split = ['4'],
    #                             use_frequency = True,
    #                             use_noise=False)

    # {"A_Create Application": "0", "A_Submitted": "1", "W_Handle leads": "2", "W_Complete application": "3", "A_Concept": "4", "A_Accepted": "5", "O_Create Offer": "6", "O_Created": "7", "O_Sent (mail and online)": "8", "W_Call after offers": "9", "A_Complete": "a", "W_Validate application": "b", "A_Validating": "c", "O_Returned": "d", "W_Call incomplete files": "e", "A_Incomplete": "f", "O_Accepted": "g", "A_Pending": "h", "A_Cancelled": "i", "O_Cancelled": "j", "A_Denied": "k", "O_Refused": "l", "O_Sent (online only)": "m"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2017_3_cases',
    #                                './real_logs/bpi_challenge_2017_3_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2017_3_cases',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split=['9'],
    #                             use_frequency=True,
    #                             use_noise=False)

    ##############################################################################################################
    ##############################################################################################################
    ##############################################################################################################
    # TODO: Experiments with Noise
    ##############################################################################################################
    ##############################################################################################################
    ##############################################################################################################

    # {"A_SUBMITTED": "0", "A_PARTLYSUBMITTED": "1", "A_DECLINED": "2", "A_PREACCEPTED": "3", "W_Completeren aanvraag": "4", "A_CANCELLED": "5", "W_Afhandelen leads": "6", "A_ACCEPTED": "7", "O_SELECTED": "8", "A_FINALIZED": "9", "O_CREATED": "a", "O_SENT": "b", "W_Nabellen offertes": "c", "O_SENT_BACK": "d", "W_Valideren aanvraag": "e", "O_DECLINED": "f", "O_CANCELLED": "g", "W_Beoordelen fraude": "h", "O_ACCEPTED": "i", "A_REGISTERED": "j", "A_ACTIVATED": "k", "A_APPROVED": "l", "W_Nabellen incomplete dossiers": "m"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2012_3_cases_01_noise',
    #                                './real_logs/bpi_challenge_2012_3_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2012_3_cases_01_noise',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split = ['4'],
    #                             use_frequency = True,
    #                             use_noise=False)

    # {"A_Create Application": "0", "A_Submitted": "1", "W_Handle leads": "2", "W_Complete application": "3", "A_Concept": "4", "A_Accepted": "5", "O_Create Offer": "6", "O_Created": "7", "O_Sent (mail and online)": "8", "W_Call after offers": "9", "A_Complete": "a", "W_Validate application": "b", "A_Validating": "c", "O_Returned": "d", "W_Call incomplete files": "e", "A_Incomplete": "f", "O_Accepted": "g", "A_Pending": "h", "A_Cancelled": "i", "O_Cancelled": "j", "A_Denied": "k", "O_Refused": "l", "O_Sent (online only)": "m"}
    apply_pipeline_to_folder([('real_logs/bpi_challenge_2017_3_cases_01_noise',
                                   './real_logs/bpi_challenge_2017_3_cases_per_variant_shortened_labels.xes.gz')],
                                'bpi_challenge_2017_3_cases_01_noise_missing_configs',
                                PipelineVariant.VARIANTS,
                                labels_to_split=['9'],
                                use_frequency=True,
                                use_noise=False)

    # {"ER Registration": "0", "Leucocytes": "1", "CRP": "2", "LacticAcid": "3", "ER Triage": "4", "ER Sepsis Triage": "5", "IV Liquid": "6", "IV Antibiotics": "7", "Admission NC": "8", "Release A": "9", "Return ER": "a", "Admission IC": "b", "Release B": "c", "Release C": "d", "Release D": "e", "Release E": "f"}
    # apply_pipeline_to_folder([('real_logs/sepsis_01_noise',
    #                            './real_logs/sepsis_shortened_labels.xes.gz')],
    #                          'sepsis_01_noise',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['1'],
    #                          use_frequency=True,
    #                          use_noise=False)


    # {"A_Create Application": "0", "A_Submitted": "1", "W_Handle leads": "2", "W_Complete application": "3", "A_Concept": "4", "A_Accepted": "5", "O_Create Offer": "6", "O_Created": "7", "O_Sent (mail and online)": "8", "W_Call after offers": "9", "A_Complete": "a", "W_Validate application": "b", "A_Validating": "c", "O_Returned": "d", "W_Call incomplete files": "e", "A_Incomplete": "f", "O_Accepted": "g", "A_Pending": "h", "A_Cancelled": "i", "O_Cancelled": "j", "A_Denied": "k", "O_Refused": "l", "O_Sent (online only)": "m", "W_Assess potential fraud": "n", "W_Shortened completion": "o"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2017_2_cases_01_noise',
    #                                './real_logs/bpi_challenge_2017_2_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2017_2_cases_01_noise',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split=['9'],
    #                             use_frequency=True,
    #                             use_noise=False)

    # {"A_SUBMITTED": "0", "A_PARTLYSUBMITTED": "1", "A_DECLINED": "2", "A_PREACCEPTED": "3", "W_Completeren aanvraag": "4", "A_CANCELLED": "5", "W_Afhandelen leads": "6", "A_ACCEPTED": "7", "O_SELECTED": "8", "A_FINALIZED": "9", "O_CREATED": "a", "O_SENT": "b", "W_Nabellen offertes": "c", "O_SENT_BACK": "d", "W_Valideren aanvraag": "e", "O_DECLINED": "f", "O_CANCELLED": "g", "O_ACCEPTED": "h", "A_ACTIVATED": "i", "A_APPROVED": "j", "A_REGISTERED": "k", "W_Beoordelen fraude": "l", "W_Nabellen incomplete dossiers": "m"}
    # apply_pipeline_to_folder([('real_logs/bpi_challenge_2012_2_cases_01_noise',
    #                                './real_logs/bpi_challenge_2012_2_cases_per_variant_shortened_labels.xes.gz')],
    #                             'bpi_challenge_2012_2_cases_01_noise',
    #                             PipelineVariant.VARIANTS,
    #                             labels_to_split = ['4'],
    #                             use_frequency = True,
    #                             use_noise=False)

    # apply_pipeline_to_folder([('real_logs/road_traffic_fines_01_noise',
    #                            './real_logs/Road_Traffic_Fine_Management_Process_shortened_labels.xes.gz')],
    #                          'road_traffic_01_noise',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['F'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # {"Confirmation of receipt": "0", "T02 Check confirmation of receipt": "1", "T03 Adjust confirmation of receipt": "2", "T06 Determine necessity of stop advice": "3", "T10 Determine necessity to stop indication": "4", "T04 Determine confirmation of receipt": "5", "T05 Print and send confirmation of receipt": "6", "T16 Report reasons to hold request": "7", "T17 Check report Y to stop indication": "8", "T19 Determine report Y to stop indication": "9", "T20 Print report Y to stop indication": "a", "T11 Create document X request unlicensed": "b", "T12 Check document X request unlicensed": "c", "T14 Determine document X request unlicensed": "d", "T15 Print document X request unlicensed": "e", "T07-1 Draft intern advice aspect 1": "f", "T08 Draft and send request for advice": "g", "T09-1 Process or receive external advice from party 1": "h", "T07-5 Draft intern advice aspect 5": "i", "T09-4 Process or receive external advice from party 4": "j", "T07-3 Draft intern advice hold for aspect 3": "k", "T07-4 Draft internal advice to hold for type 4": "l", "T07-2 Draft intern advice aspect 2": "m", "T13 Adjust document X request unlicensed": "n", "T09-3 Process or receive external advice from party 3": "o", "T18 Adjust report Y to stop indicition": "p", "T09-2 Process or receive external advice from party 2": "q"}
    # apply_pipeline_to_folder([('real_logs/environmental_permit_01_noise',
    #                            './real_logs/environmental_permit_shortened_labels.xes.gz')],
    #                          'environmental_permit_01_noise',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['3'],
    #                          use_frequency=True,
    #                          use_noise=False)

    return




    # apply_pipeline_to_folder([('real_logs/loop_start_end_same',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/loop_start_end_same_log.xes')],
    #                          'real_logs',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['B'],
    #                          use_frequency=True,
    #                          use_noise=False)

    # apply_pipeline_to_folder([('real_logs/no_loop',
    #                            '/home/jonas/repositories/pm-label-splitting/example_logs/no_loop.xes')],
    #                          'real_logs',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=['B'],
    #                          use_frequency=True,
    #                          use_noise=False)


    for path, prefix in input_paths:
        input_list = get_tuples_for_folder(path, prefix)[::-1]
        apply_pipeline_to_folder(input_list, prefix, PipelineVariant.EVENTS, labels_to_split=[], use_noise=False,
                                 use_frequency=True)

    # mrt07_0946_list = get_tuples_for_folder(
    #     '/home/jonas/repositories/pm-label-splitting/example_logs/imprInLoop_adaptive_OD/mrt07-0946/logs/',
    #     'mrt07-0946')
    #
    # apply_pipeline_to_folder(mrt07_0946_list[1:],
    #                          'mrt07-0946',
    #                          PipelineVariant.VARIANTS,
    #                          labels_to_split=[],
    #                          use_frequency=False,
    #                          use_noise=False)
    #


def apply_pipeline_to_folder(input_list, folder_name, pipeline_variant, labels_to_split=None, use_frequency=True,
                             use_noise=True):
    if labels_to_split is None:
        labels_to_split = []
    header = [
        'Name', 'max_number_of_traces', 'labels_to_split', 'original labels', 'original_precision', 'original_simplicity',
        'original_generalization', 'original_fitness' ,'Xixi number of Clusters found', 'Xixi Precision', 'Xixi ARI',
        'use_combined_context', 'use_frequency', 'window_size', 'distance_metric', 'threshold', 'Number of Clusters found',
        'Precision Align', 'ARI', 'Simplicity', 'Generalization', 'Fitness', 'Runtime']

    # Path(f'./results/{folder_name}').mkdir(parents=True, exist_ok=True)
    Path(f'./outputs/{folder_name}').mkdir(parents=True, exist_ok=True)
    # for (name, path) in input_list:
    #     log = xes_importer.apply(path, parameters={
    #         xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: 5000000})
    #     net, initial_marking, final_marking = inductive_miner.apply(log,
    #                                                                 variant=inductive_miner.Variants.IMf,
    #                                                                 parameters={inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD: 0.1})
    #     # alignment_fitness = replay_fitness_evaluator.apply(log, net, initial_marking, final_marking,
    #     #                                                    variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED)
    #     # print('alignment_fitness')
    #     # print(alignment_fitness)
    #
    #     precision = precision_evaluator.apply(log, net, initial_marking, final_marking,
    #                                           variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
    #     print('precision')
    #     print(precision)
    #     simplicity = simplicity_evaluator.apply(net)
    #     print('simplicity')
    #     print(simplicity)
    #     pnml_exporter.apply(net,
    #                         initial_marking,
    #                         f'/mnt/c/Users/Jonas/OneDrive/RWTH/BA thesis/results_real_log/road_traffic_original_real_labels.pnml',
    #                         final_marking=final_marking)
    # return

    csv_file_path = Path(f'./results/{folder_name}_{pipeline_variant}_NEW.csv')
    if csv_file_path.is_file():
        print(csv_file_path)
        print('Warning: File already existis exiting')
        return

    with open(f'./results/{folder_name}_{pipeline_variant}_NEW.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    # parsed_logs = {'mrt08-2107': {'G_1', 'P_1', 'AB_1', 'O_1', 'AA_1', 'M_1', 'H_1', 'AE_1', 'W_1', 'U_1', 'F_1', 'I_1', 'Y_1', 'N_1', 'V_1', 'X_1', 'Z_1', 'AC_1'}, 'mrt06-2142': {'A_1', 'L_1', 'T_1', 'C_1', 'AD_1', 'AQ_1', 'AB_1', 'AA_1', 'AF_1', 'J_1', 'B_1', 'AL_1', 'AI_1', 'AM_1', 'V_1'}, 'mrt08-0846': {'A_1', 'E_1', 'AD_1', 'AP_1', 'D_1', 'R_1', 'AF_1', 'B_1', 'AG_1', 'AK_1', 'C_1', 'AJ_1', 'I_1', 'V_1', 'W_1', 'AH_1', 'T_1', 'AB_1', 'O_1', 'AA_1', 'AE_1', 'AL_1', 'AI_1', 'K_1'}, 'mrt09-1233': {'E_1', 'R_1', 'D_1', 'AF_1', 'B_1', 'CG_1', 'BC_1', 'Q_1', 'AG_1', 'AJ_1', 'BQ_1', 'BW_1', 'BX_1', 'BE_1', 'W_1', 'AH_1', 'AM_1', 'Y_1', 'CE_1', 'BI_1', 'CK_1', 'AN_1', 'AB_1', 'M_1', 'BL_1', 'BJ_1', 'BY_1', 'CD_1', 'K_1'}, 'mrt03-1655': {'ED_1', 'DE_1', 'CL_1', 'BK_1', 'BC_1', 'EW_1', 'DT_1', 'CJ_1', 'BH_1', 'FW_1', 'DN_1', 'GN_1', 'BQ_1', 'CF_1', 'GC_1', 'EF_1', 'CO_1', 'CS_1', 'FY_1', 'BX_1', 'BE_1', 'EM_1', 'AM_1', 'FM_1', 'GA_1', 'N_1', 'DU_1', 'AN_1', 'FH_1', 'CP_1', 'AO_1', 'EY_1', 'AE_1', 'BP_1'}, 'mrt07-1207': {'AD_1', 'AP_1', 'R_1', 'S_1', 'AJ_1', 'AS_1', 'H_1', 'U_1', 'AH_1', 'AR_1', 'AB_1', 'O_1', 'AA_1', 'M_1', 'J_1', 'AL_1', 'K_1', 'X_1', 'AC_1'}, 'mrt03-2247': {'AK_1', 'AP_1', 'AQ_1', 'BX_1', 'BB_1', 'CN_1', 'AG_1'}, 'mrt08-2232': {'V_1', 'G_1', 'C_1', 'AJ_1', 'P_1', 'O_1', 'AT_1', 'R_1', 'M_1', 'H_1', 'U_1', 'F_1', 'AR_1', 'K_1'}, 'mrt06-1652': {'E_1', 'D_1', 'CG_1', 'DB_1', 'CI_1', 'AW_1', 'BF_1', 'C_1', 'DH_1', 'DN_1', 'BQ_1', 'DA_1', 'CT_1', 'BW_1', 'CO_1', 'CC_1', 'BX_1', 'W_1', 'Y_1', 'CE_1', 'CK_1', 'AV_1', 'Z_1', 'DD_1', 'BL_1', 'CD_1', 'BD_1', 'X_1'}, 'mrt04-1713': {'A_1', 'AD_1', 'AU_1', 'AP_1', 'Q_1', 'AK_1', 'I_1', 'V_1', 'AQ_1', 'W_1', 'U_1', 'AH_1', 'Y_1', 'N_1', 'AN_1', 'G_1', 'T_1', 'AB_1', 'O_1', 'M_1', 'AL_1', 'AI_1', 'AO_1', 'K_1', 'X_1'}, 'mrt08-1202': {'A_1', 'V_1', 'C_1', 'P_1', 'AB_1', 'O_1', 'AA_1', 'B_1', 'W_1', 'U_1', 'F_1', 'S_1', 'Y_1', 'N_1', 'AE_1'}, 'mrt04-1632': {'A_1', 'CB_1', 'AP_1', 'BR_1', 'DK_1', 'BM_1', 'BS_1', 'BF_1', 'CR_1', 'CU_1', 'I_1', 'DV_1', 'ER_1', 'DA_1', 'BW_1', 'BV_1', 'CC_1', 'CS_1', 'EI_1', 'H_1', 'BE_1', 'W_1', 'AM_1', 'BU_1', 'CV_1', 'CE_1', 'BI_1', 'L_1', 'AV_1', 'EG_1', 'G_1', 'AZ_1', 'AB_1', 'DX_1', 'CX_1', 'AI_1', 'DW_1', 'AO_1', 'BJ_1', 'CD_1', 'X_1', 'AC_1'}, 'feb18-1515': {'E_1', 'T_1', 'J_1', 'F_1', 'N_1'}, 'mrt06-1911': {'E_1', 'P_1', 'AF_1', 'F_1', 'AG_1', 'Q_1', 'AK_1', 'I_1', 'H_1', 'U_1', 'Y_1', 'L_1', 'G_1', 'T_1', 'O_1', 'M_1', 'AL_1', 'AE_1', 'X_1', 'AC_1'}, 'mrt09-1041': {'BF_1', 'C_1', 'E_1', 'AK_1', 'AP_1', 'AT_1', 'AF_1', 'B_1', 'AX_1', 'BE_1', 'W_1', 'AM_1', 'Q_1', 'AE_1', 'X_1'}, 'mrt09-1441': {'DF_1', 'CM_1', 'BR_1', 'S_1', 'BS_1', 'BF_1', 'C_1', 'AK_1', 'BZ_1', 'DH_1', 'CF_1', 'DQ_1', 'BX_1', 'CV_1', 'AR_1', 'CY_1', 'G_1', 'T_1', 'O_1', 'BJ_1', 'CH_1'}, 'mrt09-2247': {'E_1', 'P_1', 'CB_1', 'DE_1', 'BK_1', 'F_1', 'CG_1', 'AW_1', 'EL_1', 'AJ_1', 'DN_1', 'DQ_1', 'DL_1', 'DR_1', 'AR_1', 'DC_1', 'M_1', 'EX_1', 'DD_1', 'DM_1', 'CH_1', 'K_1'}, 'feb17-1236': {'R_1', 'U_1'}, 'mrt04-1607': {'A_1', 'L_1', 'R_1'}, 'feb17-1101': {'K_1'}, 'mrt07-0946': {'A_1', 'E_1', 'P_1', 'AB_1', 'AD_1', 'D_1', 'AA_1', 'J_1', 'AF_1', 'W_1', 'U_1', 'Y_1', 'AG_1', 'V_1', 'X_1'}, 'mrt09-1956': {'AP_1', 'CQ_1', 'DP_1', 'S_1', 'EC_1', 'BA_1', 'CU_1', 'CT_1', 'DL_1', 'CC_1', 'W_1', 'U_1', 'CV_1', 'DU_1', 'AN_1', 'CX_1', 'AO_1', 'BD_1', 'BP_1'}, 'feb17-0936': {'E_1'}, 'mrt07-1957': {'AJ_1', 'AB_1', 'J_1', 'B_1', 'AM_1'}, 'mrt08-1656': {'T_1', 'AB_1', 'D_1', 'AA_1', 'R_1', 'AF_1', 'AL_1', 'U_1', 'F_1', 'X_1'}, 'mrt09-0930': {'BH_1', 'AB_1', 'AU_1', 'AP_1', 'AA_1', 'AQ_1', 'J_1', 'H_1', 'BL_1', 'AI_1', 'U_1', 'S_1', 'BJ_1', 'AR_1'}, 'feb29-1654': {'H_1'}, 'feb17-1147': {'S_1', 'V_1', 'R_1'}, 'feb27-1517': {'B_1', 'C_1'}, 'feb16-1625': {'P_1', 'O_1', 'D_1', 'J_1', 'H_1'}, 'mrt06-2056': {'C_1', 'R_1', 'B_1', 'AL_1', 'AM_1', 'Y_1', 'AS_1', 'AG_1', 'X_1'}, 'feb18-1645': {'W_1'}, 'mrt04-0910': {'E_1', 'I_1', 'Z_1'}, 'feb29-1548': {'K_1', 'R_1'}}
    parsed_xixi_logs = {'mrt08-1202': {'S_1', 'O_1', 'N_1', 'I_1', 'B_1', 'P_1', 'W_1', 'Q_1', 'AH_1', 'Z_1', 'F_1', 'C_1', 'Y_1', 'AA_1', 'E_1', 'U_1', 'AG_1', 'AD_1', 'J_1', 'AE_1', 'A_1', 'AB_1', 'V_1'}, 'mrt09-1441': {'S_1', 'CV_1', 'O_1', 'BS_1', 'T_1', 'CH_1', 'AR_1', 'C_1', 'CM_1', 'CY_1', 'BJ_1', 'BX_1', 'BF_1', 'DH_1', 'CF_1', 'BR_1', 'BZ_1', 'G_1', 'DF_1', 'AK_1', 'DQ_1'}, 'mrt08-0846': {'O_1', 'AJ_1', 'I_1', 'R_1', 'B_1', 'D_1', 'W_1', 'AH_1', 'T_1', 'AP_1', 'AF_1', 'C_1', 'AL_1', 'AA_1', 'E_1', 'AG_1', 'AD_1', 'K_1', 'AE_1', 'A_1', 'AI_1', 'AK_1', 'AB_1', 'V_1'}, 'mrt09-1233': {'BB_1', 'AJ_1', 'R_1', 'CL_1', 'B_1', 'D_1', 'BI_1', 'W_1', 'CK_1', 'BK_1', 'BC_1', 'Q_1', 'CD_1', 'T_1', 'CJ_1', 'AH_1', 'BW_1', 'AR_1', 'AF_1', 'C_1', 'CE_1', 'Y_1', 'BY_1', 'AL_1', 'BE_1', 'BL_1', 'AA_1', 'E_1', 'BJ_1', 'BX_1', 'AG_1', 'CF_1', 'J_1', 'K_1', 'AQ_1', 'AM_1', 'L_1', 'AO_1', 'AI_1', 'BQ_1', 'AB_1', 'AN_1', 'CG_1', 'M_1'}, 'mrt06-1911': {'O_1', 'I_1', 'P_1', 'AC_1', 'Q_1', 'T_1', 'H_1', 'AF_1', 'F_1', 'Y_1', 'AL_1', 'E_1', 'U_1', 'AG_1', 'X_1', 'L_1', 'G_1', 'AE_1', 'AK_1', 'M_1'}, 'feb17-1147': {'S_1', 'R_1', 'V_1'}, 'mrt06-2142': {'AQ_1', 'AM_1', 'L_1', 'AA_1', 'A_1', 'T_1', 'J_1', 'B_1', 'Z_1', 'AF_1', 'AI_1', 'V_1', 'AB_1', 'C_1', 'AG_1', 'AD_1', 'Y_1', 'AL_1'}, 'mrt03-1655': {'N_1', 'DZ_1', 'R_1', 'CL_1', 'EM_1', 'EW_1', 'DT_1', 'W_1', 'BC_1', 'GC_1', 'CP_1', 'CJ_1', 'BT_1', 'DN_1', 'FY_1', 'FL_1', 'BE_1', 'GN_1', 'ED_1', 'GA_1', 'BX_1', 'BP_1', 'FM_1', 'J_1', 'EQ_1', 'AM_1', 'L_1', 'AE_1', 'DE_1', 'EX_1', 'DU_1', 'BQ_1', 'GL_1'}, 'mrt09-2247': {'AJ_1', 'DM_1', 'DR_1', 'DD_1', 'P_1', 'DL_1', 'BK_1', 'DN_1', 'CH_1', 'AR_1', 'F_1', 'AW_1', 'DC_1', 'E_1', 'K_1', 'DE_1', 'CB_1', 'EX_1', 'DQ_1', 'EL_1', 'CG_1', 'M_1'}, 'feb27-1517': {'K_1', 'L_1', 'G_1', 'I_1', 'A_1', 'B_1', 'P_1', 'D_1', 'F_1', 'C_1'}, 'mrt04-1632': {'CV_1', 'N_1', 'BV_1', 'I_1', 'CX_1', 'CC_1', 'CR_1', 'AC_1', 'BI_1', 'W_1', 'DA_1', 'EI_1', 'BS_1', 'BU_1', 'CD_1', 'H_1', 'AP_1', 'BW_1', 'DY_1', 'F_1', 'CE_1', 'BA_1', 'BE_1', 'DV_1', 'DX_1', 'AV_1', 'CU_1', 'E_1', 'BJ_1', 'BX_1', 'BF_1', 'CS_1', 'BM_1', 'BR_1', 'X_1', 'AM_1', 'L_1', 'EG_1', 'G_1', 'A_1', 'CB_1', 'AZ_1', 'CI_1', 'AO_1', 'AI_1', 'AB_1', 'ER_1', 'DK_1', 'DW_1', 'BH_1'}, 'mrt09-1041': {'AT_1', 'BE_1', 'X_1', 'AM_1', 'AE_1', 'Q_1', 'B_1', 'E_1', 'AP_1', 'AF_1', 'AX_1', 'AK_1', 'BF_1', 'C_1', 'W_1'}, 'mrt09-1956': {'CV_1', 'S_1', 'CX_1', 'CC_1', 'W_1', 'DL_1', 'CQ_1', 'AP_1', 'EC_1', 'BA_1', 'CT_1', 'CU_1', 'U_1', 'BP_1', 'AO_1', 'DU_1', 'BD_1', 'DP_1', 'AN_1'}, 'mrt07-1207': {'S_1', 'O_1', 'AJ_1', 'R_1', 'AC_1', 'AS_1', 'W_1', 'Q_1', 'AH_1', 'H_1', 'AP_1', 'AR_1', 'AL_1', 'AA_1', 'U_1', 'AD_1', 'J_1', 'K_1', 'X_1', 'AB_1', 'M_1'}, 'mrt03-2247': {'AQ_1', 'O_1', 'BB_1', 'CY_1', 'AP_1', 'CI_1', 'BX_1', 'AK_1', 'CN_1', 'AN_1', 'BY_1'}, 'feb16-1625': {'I_1', 'P_1', 'J_1'}, 'feb29-1614': {'G_1', 'I_1', 'H_1', 'C_1', 'J_1'}, 'feb29-1548': {'K_1', 'R_1'}, 'mrt09-0930': {'AU_1', 'AQ_1', 'S_1', 'BL_1', 'AA_1', 'H_1', 'BJ_1', 'U_1', 'AP_1', 'AR_1', 'AI_1', 'AB_1', 'BH_1', 'J_1'}, 'feb18-1645': {'W_1', 'X_1', 'V_1'}, 'mrt08-2107': {'O_1', 'X_1', 'N_1', 'AA_1', 'AE_1', 'I_1', 'G_1', 'H_1', 'U_1', 'Z_1', 'P_1', 'AB_1', 'AC_1', 'F_1', 'V_1', 'W_1', 'Y_1', 'M_1'}, 'mrt08-2232': {'K_1', 'AT_1', 'O_1', 'AJ_1', 'G_1', 'R_1', 'H_1', 'AR_1', 'U_1', 'P_1', 'V_1', 'F_1', 'C_1', 'M_1'}, 'feb18-1515': {'N_1', 'R_1', 'T_1', 'E_1', 'P_1', 'F_1', 'J_1'}, 'mrt06-1652': {'DB_1', 'CC_1', 'DD_1', 'D_1', 'CO_1', 'W_1', 'DA_1', 'CK_1', 'CD_1', 'DN_1', 'BW_1', 'Z_1', 'C_1', 'CE_1', 'CT_1', 'Y_1', 'AW_1', 'BL_1', 'E_1', 'BX_1', 'BF_1', 'DH_1', 'X_1', 'CI_1', 'BQ_1', 'BD_1', 'AV_1', 'CG_1'}, 'mrt07-0946': {'I_1', 'P_1', 'D_1', 'W_1', 'T_1', 'H_1', 'AF_1', 'F_1', 'Y_1', 'AA_1', 'E_1', 'U_1', 'AG_1', 'AD_1', 'J_1', 'X_1', 'L_1', 'G_1', 'A_1', 'V_1', 'AB_1'}, 'mrt06-2056': {'AM_1', 'X_1', 'R_1', 'C_1', 'B_1', 'AS_1', 'AG_1', 'Y_1', 'AL_1'}, 'mrt08-1656': {'X_1', 'AA_1', 'G_1', 'T_1', 'R_1', 'U_1', 'AF_1', 'AK_1', 'D_1', 'AB_1', 'F_1', 'C_1', 'Y_1', 'AL_1'}, 'mrt04-1713': {'O_1', 'N_1', 'I_1', 'W_1', 'Q_1', 'AH_1', 'T_1', 'AP_1', 'Y_1', 'AL_1', 'AU_1', 'U_1', 'AD_1', 'K_1', 'AQ_1', 'X_1', 'G_1', 'A_1', 'AO_1', 'AI_1', 'AK_1', 'V_1', 'AB_1', 'AN_1', 'M_1'}, 'feb17-1236': {'U_1', 'R_1'}, 'mrt07-1957': {'AM_1', 'N_1', 'AJ_1', 'A_1', 'B_1', 'AB_1', 'AG_1', 'Y_1', 'J_1'}, 'feb29-1439': {'G_1', 'I_1', 'Q_1', 'R_1', 'T_1', 'B_1', 'P_1', 'F_1', 'C_1'}, 'feb29-1334': {'Q_1', 'S_1', 'T_1', 'R_1'}, 'mrt04-1607': {'A_1', 'L_1'}, 'feb17-1101': {'K_1'}, 'feb17-0936': {'E_1', 'H_1'}, 'mrt04-0910': {'E_1', 'Z_1'}}
    parsed_variant_logs = {'mrt08-1202': {'S_1', 'AA_1', 'A_1', 'AB_1', 'W_1'}, 'mrt09-1441': {'S_1', 'CV_1', 'O_1', 'BS_1', 'T_1', 'CH_1', 'AR_1', 'C_1', 'CM_1', 'CY_1', 'BJ_1', 'BX_1', 'BF_1', 'DH_1', 'CF_1', 'BR_1', 'BZ_1', 'G_1', 'DF_1', 'AK_1', 'DQ_1'}, 'mrt08-0846': {'AE_1', 'AH_1', 'AF_1', 'AI_1', 'V_1', 'AB_1', 'AD_1'}, 'feb17-1147': {'S_1', 'R_1', 'V_1'}, 'mrt06-2142': {'AQ_1', 'AM_1', 'L_1', 'AA_1', 'J_1', 'B_1', 'AF_1', 'AI_1', 'AB_1', 'C_1', 'AL_1'}, 'mrt09-2247': {'AJ_1', 'DM_1', 'DR_1', 'DD_1', 'P_1', 'DL_1', 'BK_1', 'DN_1', 'CH_1', 'AR_1', 'F_1', 'AW_1', 'DC_1', 'E_1', 'K_1', 'DE_1', 'CB_1', 'EX_1', 'DQ_1', 'EL_1', 'CG_1', 'M_1'}, 'mrt04-1632': {'CV_1', 'BV_1', 'I_1', 'CX_1', 'CC_1', 'AC_1', 'BI_1', 'W_1', 'DA_1', 'EI_1', 'BS_1', 'BU_1', 'CD_1', 'H_1', 'AP_1', 'BW_1', 'CE_1', 'BE_1', 'AV_1', 'CU_1', 'BJ_1', 'BF_1', 'CS_1', 'BM_1', 'BR_1', 'X_1', 'AM_1', 'L_1', 'EG_1', 'G_1', 'A_1', 'CB_1', 'AZ_1', 'AO_1', 'AI_1', 'AB_1', 'ER_1', 'DK_1', 'DW_1', 'DX_1'}, 'mrt09-1233': {'CK_1', 'BL_1', 'BW_1', 'BJ_1', 'BX_1', 'AB_1', 'CG_1', 'M_1'}, 'mrt09-1041': {'AT_1', 'X_1', 'Q_1', 'B_1', 'E_1', 'AP_1', 'AF_1', 'AX_1', 'W_1'}, 'mrt03-1655': {'FH_1', 'CS_1', 'CO_1'}, 'mrt09-1956': {'CV_1', 'S_1', 'CX_1', 'CC_1', 'W_1', 'DL_1', 'CQ_1', 'AP_1', 'EC_1', 'BA_1', 'CT_1', 'CU_1', 'U_1', 'BP_1', 'AO_1', 'DU_1', 'BD_1', 'DP_1', 'AN_1'}, 'feb16-1625': {'O_1', 'H_1', 'P_1', 'D_1', 'J_1'}, 'feb29-1548': {'K_1', 'R_1'}, 'mrt09-0930': {'AU_1', 'AQ_1', 'S_1', 'BL_1', 'AA_1', 'H_1', 'BJ_1', 'U_1', 'AP_1', 'AR_1', 'AI_1', 'AB_1', 'BH_1', 'J_1'}, 'mrt08-2107': {'O_1', 'X_1', 'N_1', 'AA_1', 'AE_1', 'I_1', 'G_1', 'H_1', 'U_1', 'Z_1', 'P_1', 'AB_1', 'AC_1', 'F_1', 'V_1', 'W_1', 'Y_1', 'M_1'}, 'mrt06-1652': {'DB_1', 'CC_1', 'DD_1', 'D_1', 'CO_1', 'W_1', 'DA_1', 'CK_1', 'CD_1', 'DN_1', 'BW_1', 'Z_1', 'C_1', 'CE_1', 'CT_1', 'Y_1', 'AW_1', 'BL_1', 'E_1', 'BX_1', 'BF_1', 'DH_1', 'X_1', 'CI_1', 'BQ_1', 'BD_1', 'AV_1', 'CG_1'}, 'mrt08-2232': {'AT_1', 'O_1', 'G_1', 'R_1', 'H_1', 'AR_1', 'U_1', 'P_1', 'V_1', 'F_1', 'C_1', 'M_1'}, 'mrt06-2056': {'AM_1', 'X_1', 'R_1', 'C_1', 'B_1', 'AS_1', 'AG_1', 'Y_1', 'AL_1'}, 'mrt08-1656': {'F_1', 'U_1', 'AL_1'}, 'mrt06-1911': {'O_1', 'L_1', 'Q_1', 'I_1', 'H_1', 'U_1', 'AF_1', 'P_1', 'AC_1', 'F_1', 'AG_1', 'Y_1', 'M_1', 'AL_1'}, 'mrt04-1713': {'O_1', 'N_1', 'I_1', 'W_1', 'Q_1', 'AH_1', 'T_1', 'AP_1', 'Y_1', 'AL_1', 'AU_1', 'U_1', 'AD_1', 'K_1', 'AQ_1', 'X_1', 'G_1', 'A_1', 'AO_1', 'AI_1', 'AK_1', 'V_1', 'AB_1', 'AN_1', 'M_1'}, 'mrt07-0946': {'AA_1', 'A_1', 'E_1', 'U_1', 'AF_1', 'W_1'}, 'feb17-1236': {'U_1', 'R_1'}, 'feb27-1517': {'C_1', 'B_1'}, 'mrt07-1957': {'AJ_1', 'AM_1', 'AB_1', 'B_1'}, 'mrt07-1207': {'K_1', 'S_1', 'X_1', 'AH_1', 'AP_1', 'AR_1', 'U_1', 'AC_1', 'AS_1', 'J_1'}, 'feb18-1515': {'N_1', 'T_1', 'E_1', 'F_1', 'J_1'}, 'mrt04-1607': {'A_1', 'R_1', 'L_1'}, 'mrt04-0910': {'E_1', 'I_1', 'Z_1'}, 'feb29-1654': {'H_1'}, 'feb18-1645': {'W_1'}, 'feb17-1101': {'K_1'}, 'feb17-0936': {'E_1'}, 'mrt03-2247': {'AQ_1'}}

    print("Starting pipeline")
    for (name, path) in input_list:
        split_name = name.split('/')
        # if (split_name[0] in parsed_variant_logs and split_name[1] in parsed_variant_logs[split_name[0]]) or (split_name[0] not in parsed_xixi_logs.keys() or split_name[1] not in parsed_xixi_logs[split_name[0]]):
        #     print(f'skipped {name}')
        #     continue

        input_data = InputData(original_input_name=name,
                               log_path=path,
                               pipeline_variant=pipeline_variant,
                               labels_to_split=labels_to_split,
                               use_frequency=use_frequency,
                               use_noise=use_noise,
                               max_number_of_traces=5000000,
                               folder_name=folder_name)

        input_data.original_log = xes_importer.apply(input_data.log_path, parameters={
            xes_importer.Variants.ITERPARSE.value.Parameters.MAX_TRACES: input_data.max_number_of_traces})
        input_data.input_name = f'{input_data.original_input_name}_{input_data.pipeline_variant}' if use_frequency else f'{input_data.original_input_name}_{input_data.pipeline_variant}'

        input_data.use_combined_context = False

        input_preprocessor = InputPreprocessor(input_data)
        input_preprocessor.preprocess_input()
        summary_file_name = f'{folder_name}_{pipeline_variant}.txt' if use_frequency else f'{folder_name}_{pipeline_variant}.txt'
        input_data.summary_file_name = summary_file_name

        if input_preprocessor.has_duplicate_xor():
            print('############## Skipped ######################')
            print('Duplicate XOR found, skipping this model')
            with open(f'./outputs/best_results/{summary_file_name}', 'a') as outfile:
                outfile.write(
                    f'´\n----------------Skipped Model {input_data.input_name} because of duplicate label ------------------------\n')
            continue

        ############################################################
        ############################################################
        # concurrent_labels = get_concurrent_labels(input_data, 0.85)
        ############################################################
        ############################################################

        concurrent_labels = []

        input_data.concurrent_labels = concurrent_labels
        print('concurrent_labels')
        print(concurrent_labels)

        best_score, best_precision, best_configs = apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(
            input_data)
        try:
            write_summary_file_with_parameters(best_configs, best_score, best_precision, name, summary_file_name)
            write_summary_file(best_score, best_precision, input_data.ground_truth_precision, name, summary_file_name,
                               input_data.xixi_precision, input_data.xixi_ari)
        except Exception as e:
            print('----------------Exception occurred while writing summary file ------------------------')
            print(repr(e))
            with open(f'./outputs/best_results/{summary_file_name}', 'a') as outfile:
                outfile.write(f'´\n----------------Exception occurred while writing summary file------------------------\n')
                outfile.write(f'{repr(e)}\n')
            continue


def apply_pipeline_multi_layer_igraph_to_log_with_multiple_parameters(input_data: InputData):
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        print(f'Starting pipeline for {input_data.input_name}')
        outfile.write(run_start_string())

    best_precision = 0
    best_score = 0
    best_configs = []
    y_f1_scores_refined = []
    x_noises = [0, 0.1, 0.2, 0.3, 0.4]
    input_data.use_frequency = True

    event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count = get_event_graphs_from_event_log(input_data.original_log, input_data.labels_to_split)

    for window_size, distance, threshold in [(3, DistanceVariant.EDIT_DISTANCE, 0.75), (5, DistanceVariant.EDIT_DISTANCE, 0.75), (5, DistanceVariant.SET_DISTANCE, 0.75), (5, DistanceVariant.MULTISET_DISTANCE, 0.75)]:
        try:
            log = copy.deepcopy(input_data.original_log)

            found_score, precision, f1_scores_refined = apply_pipeline_multi_layer_igraph_to_log(
                input_data,
                log,
                distance,
                window_size,
                threshold,
                best_score,
                event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count)
            if len(f1_scores_refined) > 0:
                y_f1_scores_refined = f1_scores_refined

            if found_score > best_score:
                best_configs = [
                    get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                      distance,
                                      input_data.labels_to_split,
                                      input_data.max_number_of_traces,
                                      input_data.log_path,
                                      threshold,
                                      window_size,
                                      use_frequency=input_data.use_frequency)]
                best_score = found_score
                best_precision = precision
            elif round(found_score, 2) == round(best_score, 2):
                best_configs.append(
                    get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                      distance,
                                      input_data.labels_to_split,
                                      input_data.max_number_of_traces,
                                      input_data.log_path,
                                      threshold,
                                      window_size,
                                      use_frequency=input_data.use_frequency))
        except Exception as e:
            print('----------------Exception occurred while running pipeline ------------------------')
            print(repr(e))
            with open(f'./outputs/best_results/{input_data.summary_file_name}', 'a') as outfile:
                outfile.write(
                    f'´\n----------------Exception occurred while running pipeline------------------------\n')
                outfile.write(f'{repr(e)}\n')
                outfile.write('Error parameters:')
                outfile.write(f'{input_data.input_name}')
                outfile.write(f'{window_size}\n')
                outfile.write(f'{threshold}\n')
                outfile.write(f'{distance}\n')
                outfile.write(f'{input_data.use_combined_context}\n')

            with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
                outfile.write(f'´\n----------------Exception occurred------------------------\n')
                outfile.write(f'{repr(e)}\n')
                outfile.write(f'{window_size}\n')
                outfile.write(f'{threshold}\n')
                outfile.write(f'{distance}\n')
                outfile.write(f'{input_data.use_combined_context}\n')
            continue

    # for label in input_data.labels_to_split:
    #     for window_size in [1, 3, 5]:
    #         for distance in [DistanceVariant.EDIT_DISTANCE,
    #                          DistanceVariant.SET_DISTANCE,
    #                          DistanceVariant.MULTISET_DISTANCE]:
    #             for threshold in [0, 0.25, 0.5, 0.75, 1]:
    #                 try:
    #                     log = copy.deepcopy(input_data.original_log)
    #
    #                     found_score, precision, f1_scores_refined = apply_pipeline_multi_layer_igraph_to_log(
    #                         input_data,
    #                         log,
    #                         distance,
    #                         window_size,
    #                         threshold,
    #                         best_score,
    #                     event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count)
    #                     if len(f1_scores_refined) > 0:
    #                         y_f1_scores_refined = f1_scores_refined
    #
    #                     if found_score > best_score:
    #                         best_configs = [
    #                             get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
    #                                               distance,
    #                                               input_data.labels_to_split,
    #                                               input_data.max_number_of_traces,
    #                                               input_data.log_path,
    #                                               threshold,
    #                                               window_size,
    #                                               use_frequency=input_data.use_frequency)]
    #                         best_score = found_score
    #                         best_precision = precision
    #                     elif round(found_score, 2) == round(best_score, 2):
    #                         best_configs.append(
    #                             get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
    #                                               distance,
    #                                               input_data.labels_to_split,
    #                                               input_data.max_number_of_traces,
    #                                               input_data.log_path,
    #                                               threshold,
    #                                               window_size,
    #                                               use_frequency=input_data.use_frequency))
    #                 except Exception as e:
    #                     print('----------------Exception occurred while running pipeline ------------------------')
    #                     print(repr(e))
    #                     with open(f'./outputs/best_results/{input_data.summary_file_name}', 'a') as outfile:
    #                         outfile.write(
    #                             f'´\n----------------Exception occurred while running pipeline------------------------\n')
    #                         outfile.write(f'{repr(e)}\n')
    #                         outfile.write('Error parameters:')
    #                         outfile.write(f'{input_data.input_name}')
    #                         outfile.write(f'{window_size}\n')
    #                         outfile.write(f'{threshold}\n')
    #                         outfile.write(f'{distance}\n')
    #                         outfile.write(f'{input_data.use_combined_context}\n')
    #
    #                     with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
    #                         outfile.write(f'´\n----------------Exception occurred------------------------\n')
    #                         outfile.write(f'{repr(e)}\n')
    #                         outfile.write(f'{window_size}\n')
    #                         outfile.write(f'{threshold}\n')
    #                         outfile.write(f'{distance}\n')
    #                         outfile.write(f'{input_data.use_combined_context}\n')
    #                     continue

    print('best_score of all iterations:')
    print(best_score)

    print('best_precision of all iterations:')
    print(best_precision)

    if len(y_f1_scores_refined) > 0:
        plot_noise_to_f1_score(x_noises, input_data.y_f1_scores_unrefined, y_f1_scores_refined, input_data.input_name)
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write('Best precision found:\n')
        outfile.write(str(best_precision))
    return best_score, best_precision, best_configs


def apply_pipeline_multi_layer_igraph_to_log(input_data: InputData,
                                             log,
                                             distance_variant: DistanceVariant,
                                             window_size: int,
                                             threshold: float,
                                             best_score: float,
                                             event_graphs, short_label_to_original_label, label_and_id_to_event, variants_to_count):
    with open(f'./outputs/{input_data.input_name}.txt', 'a') as outfile:
        outfile.write(get_config_string(clustering_variant.ClusteringVariant.COMMUNITY_DETECTION, distance_variant,
                                        input_data.labels_to_split, input_data.max_number_of_traces,
                                        input_data.log_path, threshold, window_size, input_data.use_frequency))
        start = time.time()
        if input_data.pipeline_variant == PipelineVariant.VARIANTS:
            label_splitter = LabelSplitterVariantBased(outfile,
                                                       input_data.labels_to_split,
                                                       threshold=threshold,
                                                       window_size=window_size,
                                                       distance_variant=distance_variant,
                                                       clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                       use_frequency=input_data.use_frequency,
                                                       concurrent_labels=input_data.concurrent_labels,
                                                       use_combined_context=input_data.use_combined_context,
                                                       event_graphs=event_graphs,
                                                       short_label_to_original_label=short_label_to_original_label,
                                                       label_and_id_to_event=label_and_id_to_event,
                                                       variants_to_count=variants_to_count)
        elif input_data.pipeline_variant == PipelineVariant.VARIANTS_MULTIPLEX:
            label_splitter = LabelSplitterVariantMultiplex(outfile,
                                                           input_data.labels_to_split,
                                                           threshold=threshold,
                                                           window_size=window_size,
                                                           distance_variant=distance_variant,
                                                           clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                           use_frequency=input_data.use_frequency,
                                                           use_combined_context=input_data.use_combined_context)
        else:
            label_splitter = LabelSplitterEventBased(outfile,
                                                     input_data.labels_to_split,
                                                     threshold=threshold,
                                                     window_size=window_size,
                                                     distance_variant=distance_variant,
                                                     clustering_variant=clustering_variant.ClusteringVariant.COMMUNITY_DETECTION,
                                                     use_combined_context=input_data.use_combined_context)

        split_log = label_splitter.split_labels(log)
        # split_log_clustering = filter_duplicate_xor(split_log, input_data.labels_to_split,
        #                                             label_splitter.found_clustering)
        print('Skipping duplicate XOR filter to improve performance')
        split_log_clustering = label_splitter.found_clustering

        end = time.time()
        runtime = end - start
        print('runtime')
        print(runtime)
        outfile.write(f'\nRuntime: {runtime}\n')

        outfile.write('\nPerformance split_log:\n')
        outfile.write('\nIM without threshold:\n')

        labels_to_original = label_splitter.get_split_labels_to_original_labels()

        if input_data.original_log_precision == 0:
            print('Starting to get original performance')
            final_marking, initial_marking, final_net, original_precision, original_simplicity, original_generalization, original_fitness = apply_im_without_noise(labels_to_original,
                                                                                      input_data.original_log,
                                                                                      input_data.original_log,
                                                                                      outfile,
                                                                                      label_splitter.short_label_to_original_label)
            input_data.original_log_precision = original_precision
            input_data.original_log_simplicity = original_simplicity
            input_data.original_log_generalization = original_generalization
            input_data.original_log_fitness = original_fitness
            print('finished original log calculation')

        xes_exporter.apply(split_log,
                           f'./outputs/{input_data.input_name}_{threshold}_{window_size}_{distance_variant}.xes.gz')

        final_marking, initial_marking, final_net, precision, simplicity, generalization, fitness = apply_im_without_noise(labels_to_original,
                                                                                      split_log,
                                                                                      input_data.original_log,
                                                                                      outfile,
                                                                                      label_splitter.short_label_to_original_label)

        f1_scores_refined = []
        ari_score = 0
        if input_data.ground_truth_clustering:
            ari_score = get_community_similarity(input_data.ground_truth_clustering, split_log_clustering)
        else:
            ari_score = precision
        outfile.write(f'\nAdjusted Rand Index:\n')
        outfile.write(f'{ari_score}\n\n')

        print(f'\nAdjusted Rand Index:\n')
        print(f'{ari_score}')

        with open(f'./results/{input_data.folder_name}_{input_data.pipeline_variant}_NEW.csv', 'a') as f:
            writer = csv.writer(f)
            if input_data.ground_truth_clustering:
                row = [input_data.original_input_name, input_data.max_number_of_traces,
                       ' '.join(input_data.labels_to_split),
                       ', '.join(input_data.original_labels), input_data.original_log_precision,
                       input_data.original_log_simplicity, input_data.original_log_generalization,
                       input_data.original_log_fitness,
                       len(input_data.xixi_clustering),
                       input_data.xixi_precision, input_data.xixi_ari,
                       input_data.use_combined_context, input_data.use_frequency, window_size, distance_variant, threshold,
                       len(label_splitter.found_clustering), precision, ari_score, simplicity, generalization, fitness, runtime]
            else:
                row = [input_data.original_input_name, input_data.max_number_of_traces,
                       ' '.join(input_data.labels_to_split),
                       '[]', input_data.original_log_precision,
                       input_data.original_log_simplicity, input_data.original_log_generalization,
                       input_data.original_log_fitness,
                       0, 0, 0,
                       input_data.use_combined_context, input_data.use_frequency, window_size, distance_variant, threshold,
                       len(label_splitter.found_clustering), precision, ari_score, simplicity, generalization,
                       fitness, runtime]
            writer.writerow(row)

        if ari_score > best_score:
            print(f'\nHigher Adjusted Rand Index found: {ari_score}')
            print(f'\nPrecision of found clustering: {precision}')

            if input_data.use_noise:
                outfile.write('\nIM with noise threshold:\n')
                f1_scores_refined = apply_im_with_noise_and_export(input_data.input_name, 'split_log', split_log,
                                                                   input_data.original_log,
                                                                   outfile,
                                                                   label_splitter.get_split_labels_to_original_labels(),
                                                                   label_splitter.short_label_to_original_label)
            outfile_name = f'{input_data.input_name}_{threshold}_{distance_variant}_{window_size}'

            xes_exporter.apply(split_log,
                            f'./outputs/{outfile_name}_split_log.xes.gz')
            print(f'./outputs/{outfile_name}_split_log.xes.gz')
            tree = inductive_miner.apply_tree(split_log)
            export_models_and_pngs(final_marking, initial_marking, final_net, tree, input_data.input_name, f'{input_data.input_name}_{threshold}_{distance_variant}_{window_size}_split_log')
        return ari_score, precision, f1_scores_refined
