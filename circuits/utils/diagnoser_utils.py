from collections import deque
from circuits.structures.trie import *

def finalize(diagnoses_dict, probs, outputs_names, faulty_comp_prob):
    final_diagnoses = []
    for out_str, diagnoses in diagnoses_dict.items():
        outputs = dict(zip(outputs_names, map(int, list(out_str))))
        d, obs_prob = calc_observation_diagnoses_probs(outputs, diagnoses, probs, outputs_names, faulty_comp_prob)
        final_diagnoses += d
    return final_diagnoses


def calc_observation_diagnoses_probs(outputs, diagnoses, probs, outputs_names, faulty_comp_prob):
    final_diagnoses = []
    obs_prob = observation_prob(outputs, probs)
    comp_norm = comp_normalization(diagnoses, faulty_comp_prob)
    for diagnose in diagnoses:
        diagnose_prob_assuming_obs = pow(faulty_comp_prob, len(diagnose)) / comp_norm
        final_diagnoses.append((diagnose, round(obs_prob * diagnose_prob_assuming_obs, 6)))
    return final_diagnoses, obs_prob

def calc_diagnoses_probs_given_obs_prob(diagnoses, faulty_comp_prob, obs_prob):
    final_diagnoses = []
    comp_norm = 0
    for diagnose in diagnoses:
        diagnose_prob_assuming_obs = pow(faulty_comp_prob, len(diagnose))
        comp_norm += diagnose_prob_assuming_obs
        final_diagnoses.append((diagnose, obs_prob * diagnose_prob_assuming_obs))
    return [(diagnose, round(prob / comp_norm, 6)) for diagnose,prob in final_diagnoses]


def propogate_values(values, components):
    for comp in components:
        comp.calc_output(values)


def output_string(values, outputs_names):
    outputs = [str(values[name]) for name in outputs_names]
    return ''.join(outputs)


def output_tuple(values, outputs_names):
    return tuple(values[name] for name in outputs_names)


def observation_prob(outputs, probs):
    prob = 1
    for name,p in probs.items():
        if outputs[name] == 1:
            p = 1 - p
        prob *= p
    return prob


def comp_normalization(diagnoses, faulty_comp_prob):
    return float(sum(pow(faulty_comp_prob, len(diagnose)) for diagnose in diagnoses))


def diagnoses_iterator(components):
    """
    iterate all subsets of components in lexicographic order
    this will prevent checking the same subset twice
    :param components: list of components
    :return: a diagnoses iterator in lexicographic order
    """
    queue = deque([([],-1)])
    length = len(components)
    while queue:
        subset, max_in_subset = queue.popleft()
        yield subset
        if max_in_subset == length - 1:
            continue
        for index, input in enumerate(components[max_in_subset + 1:]):
            queue.append((subset + [input], index + max_in_subset + 1))


def diagnose_obs(inputs, outputs, components, outputs_names):
    # print(f'\ndiagnosing outputs {outputs}')
    diagnoses = []
    diagnoses_trie = make_trie()

    queue = deque([([], -1)])
    length = len(components)
    while queue:
        suspected_diagnose, max_in_subset = queue.popleft()
        if check_trie_for_subsets(diagnoses_trie, suspected_diagnose):
            continue
        # print(f'checking diagnose {[comp.name for comp in suspected_diagnose]}')

        for comp in suspected_diagnose:
            comp.healthy = False
        values = inputs.copy()
        propogate_values(values, components)
        for comp in suspected_diagnose:
            comp.healthy = True

        # check consistency
        consistent = all(outputs[i] == values[name] for i,name in enumerate(outputs_names))
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses











