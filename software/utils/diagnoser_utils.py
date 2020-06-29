from collections import deque
import numpy as np
from software.sfl_diagnoser.Diagnoser import TF
from scipy.special import binom as binomial_coef
from time import time
import operator
from software.diagnosers import diagnoses_from_obs, best_obs, obs_from_diagnoses, reduction_based
from datetime import datetime

faulty_comp_prob = 0.5
# faulty_output_probs = [0.11, 0.09, 0.07, 0.05, 0.03, 0.01]
faulty_output_probs = [0.1, 0.2, 0.3, 0.4, 0.5]

def observation_lexicographic_iterator(error_dict, p):
    """
    iterate all combinations of outputs in by number of flips from original output and by lexicographic order
    this order will ensure few flips will have more probability, will prevent checking the same combinations twice
    :param error_dict: the ground outputs, where all sensors are healthy
    :param p: probability for an output flip
    :return: an observation iterator in lexicographic order, each paired with its normalized probability
    """

    tests, errors_vec = zip(*error_dict.items())
    errors_vec = list(errors_vec)
    length = len(errors_vec)
    queue = deque([(errors_vec, -1, 0)])

    old_num_of_flips = -1
    old_obs_prob = -1

    while queue:
        errors_vec, max_in_subset, num_of_flips = queue.popleft()
        obs_prob = old_obs_prob if num_of_flips == old_num_of_flips else binom(length, p, num_of_flips)
        old_obs_prob = obs_prob
        old_num_of_flips = num_of_flips

        yield dict(zip(tests, errors_vec)), obs_prob
        if max_in_subset == length - 1:
            continue
        for i in range(max_in_subset + 1, length):
            copy = errors_vec[:]
            copy[i] = 1 - copy[i]
            queue.append((copy, i, num_of_flips + 1))


def one_sided_error_observation_iterator(error_dict, p):
    """
    iterate combinations of outputs where only ones turn to zeros, by number of flips from original output and by lexicographic order
    this order will ensure few flips will have more probability, will prevent checking the same combinations twice
    :param error_dict: the ground outputs, where all sensors are healthy
    :param p: probability for an output flip
    :return: an observation iterator in lexicographic order, each paired with its normalized probability
    """

    tests, errors_vec = zip(*error_dict.items())
    errors_vec = list(errors_vec)
    queue = deque([(errors_vec, -1, 0)])
    one_indices = list(np.where([i==1 for i in errors_vec])[0])
    length = len(one_indices)

    old_num_of_flips = -1
    old_obs_prob = -1
    sum_probs = obs_normalization_one_side_error(error_dict, p)

    while queue:
        errors_vec, max_in_subset, num_of_flips = queue.popleft()
        obs_prob = old_obs_prob if num_of_flips == old_num_of_flips else pow(p,num_of_flips) / sum_probs
        old_obs_prob = obs_prob
        old_num_of_flips = num_of_flips

        yield dict(zip(tests, errors_vec)), obs_prob
        if max_in_subset == length - 1:
            continue
        for i, cell in  enumerate(one_indices[max_in_subset+1:]):
            copy = errors_vec[:]
            copy[cell] = 1 - copy[cell]
            queue.append((copy, i + max_in_subset + 1, num_of_flips + 1))


def uncertain_observation_iterator(error_dict, p, uncertain_tests):
    """
    iterate combinations of outputs where only ones turn to zeros, by number of flips from original output and by lexicographic order
    this order will ensure few flips will have more probability, will prevent checking the same combinations twice
    :param error_dict: the ground outputs, where all sensors are healthy
    :param p: probability for an output flip
    :param uncertain_tests: tests that can be flipped
    :return: an observation iterator in lexicographic order, each paired with its normalized probability
    """

    tests, errors_vec = zip(*error_dict.items())
    errors_vec = list(errors_vec)
    queue = deque([(errors_vec, -1, 0)])
    uncertain_indices = list(np.where([test in uncertain_tests for test in tests])[0])
    length = len(uncertain_indices)

    old_num_of_flips = -1
    old_obs_prob = -1
    sum_probs = obs_normalization(length, p)

    while queue:
        errors_vec, max_in_subset, num_of_flips = queue.popleft()
        obs_prob = old_obs_prob if num_of_flips == old_num_of_flips else pow(p,num_of_flips) * pow(1-p, length-num_of_flips) / sum_probs
        old_obs_prob = obs_prob
        old_num_of_flips = num_of_flips

        yield dict(zip(tests, errors_vec)), obs_prob
        if max_in_subset == length - 1:
            continue
        for i, cell in  enumerate(uncertain_indices[max_in_subset+1:]):
            copy = errors_vec[:]
            copy[cell] = 1 - copy[cell]
            queue.append((copy, i + max_in_subset + 1, num_of_flips + 1))


def binom(n,p,k):
    x = k * np.log2(p) + (n - k) * np.log2(1 - p)
    return pow(2,x)


def diagnoses_iterator(comps):
    """
    iterate all subsets of components in lexicographic order
    this will prevent checking the same subset twice
    :param comps: all components
    :return: a diagnoses iterator in lexicographic order
    """
    num_comps = len(comps)
    queue = deque([([],-1)])
    while queue:
        subset, max_in_subset = queue.popleft()
        yield subset
        if max_in_subset == num_comps - 1:
            continue
        for i, comp in  enumerate(comps[max_in_subset+1:]):
            queue.append((subset + [comp], i + max_in_subset + 1))


def obs_normalization_one_side_error(error, p):
    n = list(error.values()).count(1)
    return obs_normalization(n, p)

def obs_normalization(n, p):
    return sum(binomial_coef(n, k) * pow(p, k) * pow(1-p, n-k) for k in range(n + 1))

def observation_prob(num_of_tests, orig_failing, obs_failing, p):
    num_of_flips = len(orig_failing.symmetric_difference(obs_failing))
    # return pow(p, num_of_flips) / obs_norm
    return binom(num_of_tests, p, num_of_flips)


def calc_diagnoses_probs_given_obs_prob(diagnoses, priors, faulty_comp_prob, obs_prob):
    return [(diagnose, prob * (non_uniform_prior(diagnose, priors) if priors else pow(faulty_comp_prob, len(diagnose)))) for diagnose, prob in diagnoses]


def non_uniform_prior(comps, priors):
    prob = 1
    for comp in comps:
        prob *= priors[comp]
    return prob


def barinel(diag, matrix, error):
    return TF.TF(matrix, error, diag).maximize()

def run_all_diagnosers(inst, error, uncertain_tests, all_tests):
    alg1_result, alg1_time, alg1_best_diag_card, alg1_mean_card = run_diagnoser(inst, error, faulty_output_probs[0],
                                                                                uncertain_tests)
    print(f'\tdiags from obs: {alg1_time} seconds')
    print(f'\t\t{alg1_result}')

    alg2_result, alg2_time, alg2_best_diag_card, alg2_mean_card = run_obs_from_diagnoses(error, all_tests,
                                                                                         faulty_output_probs[0],
                                                                                         uncertain_tests)
    print(f'\tobs from diags: {alg2_time} seconds')
    print(f'\t\t{alg2_result}')

    for faulty_output_prob in faulty_output_probs:
        alg3_result, alg3_time, alg3_best_diag_card, alg3_mean_card = run_best_diagnoser(inst, error,
                                                                                         faulty_output_prob,
                                                                                         uncertain_tests)
        print(f'\tbest obs with faulty output prob of {faulty_output_prob}: {alg3_time} seconds')
        print(f'\t\t{alg3_result}')
        yield (alg1_result, alg2_result, alg3_result), (alg1_time, alg2_time, alg3_time),\
              (alg1_best_diag_card, alg2_best_diag_card, alg3_best_diag_card),\
              (alg1_mean_card, alg2_mean_card,  alg3_mean_card), faulty_output_prob


def compare_with_smart_mhs(diagnoser, error, uncertain_tests, smart_mhs_diagnoser):
    alg1_result, alg1_time, alg1_best_diag_card, alg1_mean_card = run_diagnoser(diagnoser, error, faulty_output_probs[0],
                                                                                uncertain_tests)
    print(f'\tdiags from obs (regular): {alg1_time} seconds')
    print(f'\t\t{alg1_result}')

    alg2_result, alg2_time, alg2_best_diag_card, alg2_mean_card = run_diagnoser_mhs(smart_mhs_diagnoser, faulty_output_probs[0])
    print(f'\tdiags from obs (smart mhs): {alg2_time} seconds')
    print(f'\t\t{alg2_result}')

    yield (alg1_result, alg2_result), (alg1_time, alg2_time),\
              (alg1_best_diag_card, alg2_best_diag_card), (alg1_mean_card, alg2_mean_card)


def diagnoser(func):
    def func_wrapper(*args, **kwargs):
        start = time()
        # print('time: {}'.format(datetime.now().strftime("%H:%M:%S")))
        diagnoses = func(*args, **kwargs)
        end = time()
        diagnoses = [(diagnose, round(prob, 6)) for diagnose, prob in diagnoses]
        diagnoses = sorted(diagnoses, key=operator.itemgetter(1, 0), reverse=True)
        top_diagnoses = diagnoses[:10]
        best_diag_cardinality = len(diagnoses[0][0])
        mean_cardinality = np.mean([len(d[0]) for d in diagnoses])

        p = sum(map(operator.itemgetter(1), diagnoses))
        # print(f"sum of probs: {p}")
        return top_diagnoses, end - start, best_diag_cardinality, mean_cardinality
    return func_wrapper

@diagnoser
def run_diagnoser(diagnoser, error, faulty_output_prob, uncertain_tests):
    return diagnoses_from_obs.diagnose_all_combinations(diagnoser, error, faulty_comp_prob, faulty_output_prob, uncertain_tests)

@diagnoser
def run_diagnoser_mhs(smart_mhs_diagnoser, faulty_output_prob):
    return diagnoses_from_obs.diagnose_smart_mhs(smart_mhs_diagnoser, faulty_comp_prob, faulty_output_prob)

@diagnoser
def run_best_diagnoser(diagnoser, error, faulty_output_prob, uncertain_tests):
    return best_obs.find_best_diagnoses(diagnoser, error, faulty_comp_prob, faulty_output_prob, uncertain_tests)

@diagnoser
def run_obs_from_diagnoses(diagnoser, all_tests, faulty_output_prob, uncertain_tests):
    return obs_from_diagnoses.diagnose_all_combinations(diagnoser, all_tests, faulty_comp_prob, faulty_output_prob, uncertain_tests)

@diagnoser
def run_reduction_based(diagnoser, error, faulty_output_prob, uncertain_tests):
    return reduction_based.diagnose_all_combinations(diagnoser, error, faulty_output_prob, uncertain_tests)