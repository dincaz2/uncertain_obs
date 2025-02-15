from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from software.utils.diagnoser_utils import run_all_diagnosers
import operator
import os
import csv
from random import sample

def file2tuple(file):
    ncomps,ntests,sample = list(map(int, file.split('.')[0].split('_')))
    # ncomps = ncomps + 100 if sample>10 else ncomps
    return ncomps,ntests,sample

def find_matrix_index(matrices, matrix):
    return dict(reversed(enumerate(matrices)))[matrix]

def filter_low(matrix_name):
    comps, tests = list(map(int, matrix_name.split('_')[:2]))
    # return (7 <= comps <= 9 and 10 <= tests <= 13) or (7 <= tests <= 9 and 10 <= comps <= 13)
    return comps >= 7 and tests >= 7

def pipeline(folder, output):
    matrices = [file for file in os.listdir(folder) if file.endswith('.matrix')]
    matrices = sorted(matrices, key=file2tuple) # for logic traversal of matrices. also taking only 10 samples instead of 20
    print(f'total of {len(matrices)} matrices')
    matrices = list(filter(filter_low, matrices))
    # from_matrix = '14_14_11.matrix'
    # from_index = dict(map(reversed,enumerate(matrices)))[from_matrix]
    # to_matrix = '14_14_20.matrix'
    # to_index = dict(map(reversed,enumerate(matrices)))[to_matrix]
    # matrices = matrices[from_index:to_index + 1]
    print(f'remaining {len(matrices)} matrices')
    # print(matrices[0])
    # return
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('matrix_name', 'sample', '#components', '#tests', '#failing_tests', '#uncertain_tests', 'faulty_output_prob', 'error_vector',
                         'scan_all_obs_time', 'scan_all_diags_time', 'scan_best_obs_time',
                         'scan_all_obs_best_cardinality', 'scan_all_diags_best_cardinality', 'scan_best_obs_best_cardinality',
                         'scan_all_obs_mean_cardinality', 'scan_all_diags_mean_cardinality', 'scan_best_obs_mean_cardinality',
                         'scan_all_obs_output', 'scan_all_diags_output', 'scan_best_obs_output'))
        f.flush()
        for matrix_file in matrices:
            print(f'diagnosing matrix {matrix_file}')

            inst, error, initials, _ = readPlanningFile(os.path.join(folder, matrix_file))
            error_vec = list(map(operator.itemgetter(1), sorted(error.items(), key=operator.itemgetter(0))))
            num_of_comps = len(Experiment_Data().COMPONENTS_NAMES.keys())
            all_tests = Experiment_Data().POOL.keys()
            num_of_tests = len(all_tests)
            num_failing_tests = error_vec.count(1)
            sample_num = int(matrix_file.split('.')[0].split('_')[2])
            print(f'comps: {num_of_comps}, tests: {num_of_tests}, failing: {num_failing_tests}')

            # for proportion_uncertain in [0.1, 0.3, 0.5, 0.7, 1]:
            for num_uncertain in range(7, num_of_tests + 1):
                # num_uncertain = ceil(num_of_tests * proportion_uncertain)
                uncertain_tests = sample(all_tests, num_uncertain)
                # print(f'time: {time()}')
                print(f'uncertain tests: {uncertain_tests}')

                for results, time, best_diag_card, mean_card, faulty_output_prob in run_all_diagnosers(inst, error,
                                                                                                       uncertain_tests,
                                                                                                       initials):
                    writer.writerow((matrix_file, sample_num, num_of_comps, num_of_tests, num_failing_tests, num_uncertain, faulty_output_prob, error_vec,
                                     *time, *best_diag_card, *mean_card, *results))
                    f.flush()
                print()
            print('\n\n\n')