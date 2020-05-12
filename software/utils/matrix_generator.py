import numpy as np
from software.sfl_diagnoser.Diagnoser.diagnoserUtils import write_planning_file
import random
from math import ceil
from functools import reduce
from copy import deepcopy

def generate_all():
    filename_template = '../matrices/synthetic/{}_{}_{}.matrix'
    reduced_filename_template = '../matrices/synthetic_reducted/{}_{}_{}.matrix'
    for num_comps in range(1, 15, 1):
        comps = [f'c{i}' for i in range(num_comps)]
        for num_tests in range(1, 15, 1):
            tests = [f'T{i+1}' for i in range(num_tests)]
            for sample in range(20): # num of samples for each matrix size
                matrix, error, reduced_matrix = generate_matrix(comps, tests)
                filename = filename_template.format(num_comps, num_tests, sample+1)
                test_details = [(test, trace, err) for (test,trace),err in zip(matrix.items(),error)]
                write_planning_file(filename, [], test_details)

                reduced_filename = reduced_filename_template.format(num_comps, num_tests, sample+1)
                test_details = [(test, trace, err) for (test,trace),err in zip(reduced_matrix.items(),error)]
                write_planning_file(reduced_filename, [], test_details)

                # for i in range(num_tests):
                #     trace = [comp for j,comp in enumerate(comps) if matrix[i][j] == 1]
                #     test_details.append((tests[i], trace, error[i]))



def test_or_empty(add, test):
    return [test] if add else []


def generate_matrix(comps, tests):
    comps_sample = list(range(1,len(comps)+1))
    M = {test: random.sample(comps,random.sample(comps_sample, 1)[0]) for test in tests} # generate at least one touching comp for each test
    touching_comps = set(reduce(lambda a,b: a+b, M.values()))
    while not all(comp in touching_comps for comp in comps):
        M = {test: random.sample(comps, random.sample(comps_sample, 1)[0]) for test in tests}  # generate at least one touching comp for each test
        touching_comps = set(reduce(lambda a, b: a + b, M.values()))

    reduced_M = {test: [test] +  M[test] for test in tests}

    # error = [1] * num_failing + [0] * (len(tests) - num_failing)
    # random.shuffle(error)
    num_tests = len(tests)
    error = [0] * num_tests
    while all(e == 0 for e in error):
        error = [int(round(e)) for e in np.random.random(num_tests)]
        # error = np.vectorize(round)(np.random.random(len(tests)))

    return M, error, reduced_M

def generate_matrix2(num_comps, num_tests, num_failing):
    # deprecated - some comps might not touch any test
    arr_round = np.vectorize(round)
    M = np.random.random((num_tests, num_comps)) # #comps X #tests matrix of values in [0,1)
    M = arr_round(M) # transform matrix into a binary one (only zeros and ones)

    new_M = []
    # make sure each test touches at least one comp
    for test in M:
        if not any(c for c in test):
            test[0] = 1
            random.shuffle(test)
        new_M.append(test)

    error = [1] * num_failing + [0] * (num_tests - num_failing)
    random.shuffle(error)

    return M, error

generate_all()