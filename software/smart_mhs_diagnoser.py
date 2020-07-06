from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from software.utils.diagnoser_utils import compare_with_smart_mhs
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
    min_num = 1
    max_num = 14
    return min_num <= comps <= max_num and min_num <= tests <= max_num

def pipeline(folder, output):
    matrices = [file for file in os.listdir(folder) if file.endswith('.matrix')]
    matrices = sorted(matrices, key=file2tuple) # for logic traversal of matrices.
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
        writer.writerow(('matrix_name', 'sample', '#components', '#tests', '#failing_tests', 'error_vector',
                         'o2d_time', 'o2d_mhs_time', 'o2d_best_cardinality', 'o2d_mhs_best_cardinality',
                         'o2d_mean_cardinality', 'o2d_mhs_mean_cardinality', 'o2d_output', 'o2d_mhs_output'))
        f.flush()
        for matrix_file in matrices:
            print(f'diagnosing matrix {matrix_file}')

            diagnoser, smart_mhs_diagnoser, error, initials, _ = readPlanningFile(os.path.join(folder, matrix_file))
            error_vec = list(map(operator.itemgetter(1), sorted(error.items(), key=operator.itemgetter(0))))
            num_of_comps = len(Experiment_Data().COMPONENTS_NAMES.keys())
            all_tests = Experiment_Data().POOL.keys()
            num_of_tests = len(all_tests)
            num_failing_tests = error_vec.count(1)
            sample_num = int(matrix_file.split('.')[0].split('_')[2])
            # if sample_num != 2:
            #     continue
            print(f'comps: {num_of_comps}, tests: {num_of_tests}, failing: {num_failing_tests}')

            for results, time, best_diag_card, mean_card in compare_with_smart_mhs(diagnoser, error, all_tests, smart_mhs_diagnoser):
                writer.writerow((matrix_file, sample_num, num_of_comps, num_of_tests, num_failing_tests, error_vec,
                                 *time, *best_diag_card, *mean_card, *results))
                f.flush()
            print()
            print('\n')