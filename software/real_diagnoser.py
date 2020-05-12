from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from software.utils.diagnoser_utils import run_all_diagnosers
import operator
import os
import csv

def pipeline(folder, output):
    # matrices = [a for a in
    #             ['0aa57f04ede369a4f813bbb86d3eac1ed20b084c.matrix2', '0cc451d5e5cb565eb7311308466f487bc534ebaf.matrix2',
    #              '19f33e4e0d824e732d07f06a08567c27b3c808f3.matrix2', '1c606c3d96838e595a0664cbafdd60caae34aa0e.matrix2',
    #              '229151ec41339450e4d4f857bf92ed080d3e2430.matrix', '3905071819a14403d1cdb9437d2e005adf18fc70.matrix',
    #              '3b46d611b2d595131ce0bce9bdb3209c55391be7.matrix', '3cea4b2af3f9caf6aa72fa56d647c513d320e073.matrix',
    #              '3f900a7395e31eaa72e0fa2fb43c090e5a8fa4ed.matrix', '48bf241d4149919e0928e39616bee2e3783e2987.matrix',
    #              '5209cefa81c9c48a34e5472fdcf2a308a4da2589.matrix', '575be16474e8e8246d4bbde6f243fdf38c34ad5b.matrix',
    #              '68217617c54467c7c6098168e714a2fb6a48847d.matrix', '8da5fb28a764eee26c76a5018c293f224017887b.matrix',
    #              'ac2a39e92a71d5f9eb3ca7c6cc789b6341c582a4.matrix', 'ac58807ede6d9a0625b489cdca6fd37bad9cacfe.matrix',
    #              'b2f1757bf9ec1632a940b9a2e65a1a022ba54af8.matrix', 'b5906d3f325ca3a1147d5fa68912975e2e6c347e.matrix',
    #              'b6f7a8a8be57c9525c59e9f21e958e76cee0dbaf.matrix', 'cbf8e4eb017a99af9a8f24eb8429e8a12b62af8b.matrix',
    #              'cf28c89dcf72d27573c478eb91e3b470de060edd.matrix', 'cfff06bead88e2c1bb164285f89503a919e0e27f.matrix',
    #              'e28c95ac2ce95852add84bdf3d2d9c00ac98f5de.matrix', 'ec0c4e5508dbd8af83253f7c50f8b728a1003388.matrix',
    #              'temp.matrix'] if a.endswith(matrix_file_suffix)]
    matrices = [file for file in ['19f33e4e0d824e732d07f06a08567c27b3c808f3.matrix2', '229151ec41339450e4d4f857bf92ed080d3e2430.matrix2',
                                  '3cea4b2af3f9caf6aa72fa56d647c513d320e073.matrix2', '68217617c54467c7c6098168e714a2fb6a48847d.matrix2',
                                  'ac2a39e92a71d5f9eb3ca7c6cc789b6341c582a4.matrix2', 'ac58807ede6d9a0625b489cdca6fd37bad9cacfe.matrix',
                                  'cf28c89dcf72d27573c478eb91e3b470de060edd.matrix', 'cfff06bead88e2c1bb164285f89503a919e0e27f.matrix']
                if file.endswith('.matrix')]
    # matrices = [file for file in os.listdir(folder) if file.endswith('.matrix')]
    # matrices = ['temp.matrix']
    print(f'total of {len(matrices)} matrices')
    # from_matrix = '14_14_11.matrix'
    # from_index = dict(map(reversed,enumerate(matrices)))[from_matrix]
    # to_matrix = '14_14_20.matrix'
    # to_index = dict(map(reversed,enumerate(matrices)))[to_matrix]
    # matrices = matrices[from_index:to_index + 1]
    print(f'remaining {len(matrices)} matrices')
    # print(matrices)
    # return
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('#','matrix_name', '#components', '#tests', '#components_before_cut', '#tests_before_cut', '#failing_tests', '#uncertain_tests', 'faulty_output_prob', 'error_vector',
                         'scan_all_obs_time', 'scan_all_diags_time', 'scan_best_obs_time',
                         'scan_all_obs_best_cardinality', 'scan_all_diags_best_cardinality', 'scan_best_obs_best_cardinality',
                         'scan_all_obs_mean_cardinality', 'scan_all_diags_mean_cardinality', 'scan_best_obs_mean_cardinality',
                         'scan_all_obs_output', 'scan_all_diags_output', 'scan_best_obs_output'))
        f.flush()
        for i, matrix_file in enumerate(matrices):
            print(f'diagnosing matrix {matrix_file}')

            inst, error, all_tests, (old_component, old_tests) = readPlanningFile(os.path.join(folder, matrix_file), cut=True)
            error_vec = list(map(operator.itemgetter(1), sorted(error.items(), key=operator.itemgetter(0))))
            uncertain_tests = [test for (test,outcome) in error.items() if outcome == 1]
            num_of_comps = len(Experiment_Data().COMPONENTS_NAMES.keys())
            num_of_tests = len(all_tests)
            old_num_of_comps = len(old_component)
            old_num_of_tests = len(old_tests)
            num_failing_tests = error_vec.count(1)
            num_uncertain = len(uncertain_tests)
            print(f'comps: {num_of_comps}, tests: {num_of_tests}, uncertain: {num_uncertain}, old_comps: {old_num_of_comps}, old_tests: {old_num_of_tests}')
            if num_of_comps <= 70 or num_of_comps > 100:
                print(f'skipping {matrix_file}')
                continue
            if num_uncertain < 2:
                print(f'skipping {matrix_file}')
                continue
            # continue

            for results, time, best_diag_card, mean_card, faulty_output_prob in run_all_diagnosers(inst, error, uncertain_tests, all_tests):
                writer.writerow((i, matrix_file, num_of_comps, num_of_tests, old_num_of_comps, old_num_of_tests,
                                 num_failing_tests, num_uncertain, faulty_output_prob, error_vec,
                                 *time, *best_diag_card, *mean_card, *results))
                f.flush()
            print('\n\n')