"""
Test the reduction where the tests are components as well
"""

from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from software.utils.diagnoser_utils import run_all_diagnosers, run_diagnoser, run_reduction_based
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
    return comps >= 2 and tests >= 2

def print_matrix(error):
    comps = Experiment_Data().COMPONENTS_NAMES
    comps_names = sorted(comps.values())
    reverse_comps_dict = dict([reversed(t) for t in comps.items()])
    trace = Experiment_Data().POOL
    tests_names = sorted(trace.keys())
    print('\t\\ \t|\t' + '\t|\t'.join(comps_names) + '\t|\te\t|')
    for test in tests_names:
        touching = [1 if reverse_comps_dict[c] in trace[test] else 0 for c in comps_names]
        # buggy = 1 if test in error else 0
        print(f'\t{test}\t|\t' + '\t|\t '.join(map(str, touching)) + f'\t|\t{error[test]}\t|')

def pipeline(folder, output):
    second_folder = folder + '_reducted'
    matrices = [file for file in os.listdir(folder) if file.endswith('.matrix')]
    matrices = sorted(matrices, key=file2tuple) # for logic traversal of matrices
    print(f'total of {len(matrices)} matrices')
    matrices = list(filter(filter_low, matrices))
    # matrices = list(filter(filter_low, matrices))
    # from_matrix = '14_14_11.matrix'
    # from_index = dict(map(reversed,enumerate(matrices)))[from_matrix]
    # to_matrix = '14_14_20.matrix'
    # to_index = dict(map(reversed,enumerate(matrices)))[to_matrix]
    # matrices = matrices[from_index:to_index + 1]
    print(f'remaining {len(matrices)} matrices')
    # print(matrices[0])
    # return


    for matrix_file in matrices:
        print(f'diagnosing matrix {matrix_file}')
        # matrix_file = '1_2_1.matrix'

        inst, error, initials, _ = readPlanningFile(os.path.join(folder, matrix_file), cut=True)
        # uncertain_tests = Experiment_Data().POOL.keys()
        uncertain_tests = [test for (test, outcome) in error.items() if outcome == 1]
        alg1_result, alg1_time, _, _ = run_diagnoser(inst, error, 0.1, uncertain_tests)

        inst, error, initials, _ = readPlanningFile(os.path.join(second_folder, matrix_file), cut=True)
        if len(Experiment_Data().COMPONENTS_NAMES) <= 2:
            print('small matrix. continuing')
            continue
        alg2_result, alg2_time, _, _ = run_reduction_based(inst, error, 0.1, uncertain_tests)

        alg1_diags = list(map(operator.itemgetter(0), alg1_result))
        alg2_diags = list(map(operator.itemgetter(0), alg2_result))
        if alg1_diags != alg2_diags:
            print(f'difference in {matrix_file}:')
            print(f'o2d results: {alg1_result}')
            print(f'reduction results: {alg2_result}')
            print_matrix(error)
            break