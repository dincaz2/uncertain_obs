import numpy as np
from software.sfl_diagnoser.Diagnoser.diagnoserUtils import write_planning_file
import random
from math import ceil
from functools import reduce

def generate_all():
    filename_template = 'matrices/synthetic/{}_{}_{}.matrix'
    for num_comps in range(7, 15, 1):
        comps = [f'c{i}' for i in range(num_comps)]
        for num_tests in range(7, 15, 1):
            tests = [f'T{i+1}' for i in range(num_tests)]
            for sample in range(20): # num of samples for each matrix size
                matrix, error = generate_matrix(comps, tests)
                filename = filename_template.format(num_comps, num_tests, sample+1)
                test_details = [(test, trace, err) for (test,trace),err in zip(matrix.items(),error)]
                # for i in range(num_tests):
                #     trace = [comp for j,comp in enumerate(comps) if matrix[i][j] == 1]
                #     test_details.append((tests[i], trace, error[i]))

                write_planning_file(filename, [], test_details)


def generate_matrix(comps, tests):
    comps_sample = list(range(1,len(comps)+1))
    M = {test: random.sample(comps,random.sample(comps_sample, 1)[0]) for test in tests}
    touching_comps = set(reduce(lambda a,b: a+b, M.values()))
    while not all(comp in touching_comps for comp in comps):
        M = {test: random.sample(comps, random.sample(comps_sample, 1)[0]) for test in tests}
        touching_comps = set(reduce(lambda a, b: a + b, M.values()))

    # error = [1] * num_failing + [0] * (len(tests) - num_failing)
    # random.shuffle(error)
    num_tests = len(tests)
    error = [0] * num_tests
    while all(e == 0 for e in error):
        error = [int(round(e)) for e in np.random.random(num_tests)]
        # error = np.vectorize(round)(np.random.random(len(tests)))

    return M, error

def generate_matrix2(num_comps, num_tests, num_failing):
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