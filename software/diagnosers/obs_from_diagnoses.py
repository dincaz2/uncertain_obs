from software.utils import diagnoser_utils
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from collections import defaultdict
from itertools import chain, combinations


def diagnose_all_combinations(error, test_names, faulty_comp_prob, faulty_output_prob, uncertain_tests):
    failing_tests = set(sorted(test for test,out in error.items() if out == 1))
    num_of_tests = len(error)
    diagnoses = defaultdict(list)
    obs_vectors = {}

    data = Experiment_Data()
    priors = data.PRIORS
    all_comps = data.COMPONENTS_NAMES.keys()
    comps_mapping = dict(enumerate(all_comps))
    reverse_comps_mapping = dict(zip(all_comps, range(len(all_comps))))
    test_comps = [data.POOL[test] for test in test_names]
    test_matrix = list(map(lambda test: list(map(lambda comp: 1 if comp in test else 0, all_comps)), test_comps))

    all_tests = data.POOL
    # failing_tests_dict = {test:comps for test,comps in all_tests.items() if error[test] == 1}
    uncertain_tests_dict = {test:comps for test,comps in all_tests.items() if test in uncertain_tests}
    must_pass_dict = {test:comps for test,comps in all_tests.items() if test not in uncertain_tests and error[test] == 1}

    for comps in diagnoser_utils.diagnoses_iterator(range(len(all_comps))):
        for obs in simulate(comps, reverse_comps_mapping, uncertain_tests_dict, must_pass_dict): # change to all_tests for two-sided error
            if obs not in obs_vectors:
                obs_vectors[obs] = [1 if test in obs else 0 for test in test_names]
            barinel_prob = diagnoser_utils.barinel(comps, test_matrix, obs_vectors[obs]) if obs else 1
            real_comps = tuple(comps_mapping[i] for i in comps)
            diagnoses[obs].append((real_comps, barinel_prob))

        # print(comps)



    # obs_norm = diagnoser_utils.obs_normalization(len(uncertain_tests), faulty_output_prob)
    normalized_diagnoses = [diagnoser_utils.calc_diagnoses_probs_given_obs_prob(obs_diags, priors, faulty_comp_prob, diagnoser_utils.observation_prob(num_of_tests, failing_tests, obs, faulty_output_prob)) for obs,obs_diags in diagnoses.items()]
    final_diagnoses = defaultdict(lambda:0)
    for obs_diags in normalized_diagnoses:
        for diagnose, prob in obs_diags:
            final_diagnoses[diagnose] += prob

    diagnoses_with_probs = final_diagnoses.items()
    sum_probs = sum(prob for _, prob in diagnoses_with_probs)
    return [(i2comp(diag, data.COMPONENTS_NAMES), prob / sum_probs) for diag, prob in diagnoses_with_probs]

def i2comp(diag, comps_dict):
    return tuple(comps_dict[i] for i in diag)

def simulate(comps, reverse_comps_mapping, tests, must_pass_dict):
    """
    find all observations that comps can explain (comps is a hitting set of them).
    :param comps: iterator of components names
    :param reverse_comps_mapping: dictionary mapping component name to its key
    :param tests: dictionary of tests that the observations can be generated from.
     tests can be all tests for two-sided error, failing_tests only for one-sided error or arbitrary tests for uncertainty
    :param must_pass_dict: dictionary of tests that must be in each observation
    :return: generator of sets of failing tests, denoting observations
    """

    comps = set(comps)
    # checking that comps indeed touches all must_pass tests
    if not all(comps.intersection(test_comps) for test_comps in must_pass_dict.values()):
        return None
    must_pass = set(must_pass_dict.keys())

    # projected - for each test, show only its touching components from "comps"
    must_pass_projected_tests = {test: comps.intersection(reverse_comps_mapping[comp] for comp in test_comps) for test, test_comps in must_pass_dict.items()}
    lone_tests = defaultdict(list) # mapping from component to all tests touching only this component
    lone_touching_comps = set() # set of all components that are lone-toucher of a must-pass test
    for test, test_comps in must_pass_projected_tests.items():
        if not test_comps:
            return None # there exists a must-pass test that no comp touch - no valid observations
        if len(test_comps) == 1: # lone toucher
            touching_comp = test_comps.pop()
            lone_tests[touching_comp].append(test)
            lone_touching_comps.add(touching_comp)

    projected_tests = {test: comps.intersection(reverse_comps_mapping[comp] for comp in test_comps) for test, test_comps in tests.items()}
    all_touching_tests = set()
    for test, test_comps in projected_tests.items():
        if len(test_comps) > 0:
            all_touching_tests.add(test)
            if len(test_comps) == 1:
                touching_comp = test_comps.pop()
                if touching_comp not in lone_touching_comps: # add regular test to its lone toucher component only if this component is not a lone toucher of a must-pass test
                    lone_tests[touching_comp].append(test)

    # check that all components are lone touchers for at least one test, else it can't be in a minimal hitting set
    if any(comp not in lone_tests for comp in comps):
        return None
    yield from build_combs(powerset(all_touching_tests), list(lone_tests.values()), set(), 0, must_pass)


def build_combs(all_subsets_touching, lone_tests, ret, i, must_pass):
    if i == len(lone_tests):
        for tests_subset in all_subsets_touching:
            yield tuple(sorted(ret | tests_subset | must_pass))
    else:
        for test in lone_tests[i]:
            yield from build_combs(all_subsets_touching, lone_tests, ret.union({test}), i + 1, must_pass)


def powerset(s):
    # powerset({1,2,3}) --> [{}, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3}]
    return [set(comb) for comb in chain.from_iterable(combinations(s, r) for r in range(len(s)+1))]