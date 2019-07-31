from collections import deque
import numpy as np
from software.sfl_diagnoser.Diagnoser import TF
from scipy.special import binom as binomial_coef

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
        obs_prob = old_obs_prob if num_of_flips == old_num_of_flips else pow(p,num_of_flips) / sum_probs
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
    return sum(binomial_coef(n, k) * pow(p, k) for k in range(n + 1))

def observation_prob(num_of_tests, orig_failing, obs_failing, p, obs_norm):
    num_of_flips = len(orig_failing.symmetric_difference(obs_failing))
    return pow(p, num_of_flips) / obs_norm
    # return binom(num_of_tests, p, num_of_flips)


def calc_diagnoses_probs_given_obs_prob(diagnoses, priors, faulty_comp_prob, obs_prob):
    final_diagnoses = []
    probs_sum = 0
    for diagnose, old_prob in diagnoses:
        p = non_uniform_prior(diagnose, priors) if priors else pow(faulty_comp_prob, len(diagnose))
        p *= old_prob
        probs_sum += p
        final_diagnoses.append((diagnose, obs_prob * p))
    return [(diagnose, prob / probs_sum) for diagnose,prob in final_diagnoses]


def non_uniform_prior(comps, priors):
    prob = 1
    for comp in comps:
        prob *= priors[comp]
    return prob


def barinel(diag, matrix, error):
    return TF.TF(matrix, error, diag).maximize()