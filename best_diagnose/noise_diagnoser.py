from collections import deque
from bfs_diagnose.diagnoser_utils import *
from bfs_diagnose.trie import *
from best_diagnose import prob_utils
import operator

def find_best_diagnose(inputs, components, outputs_names, faulty_comp_prob, p):
    prob_sum = 1
    max_prob_diagnose = (None, 0)
    for outputs, obs_prob in prob_utils.observation_lexicographic_iterator(outputs_names, p):
        diagnoses = diagnose(inputs, outputs, components)
        diagnoses_with_prob = calc_diagnoses_probs_given_obs_prob(diagnoses, faulty_comp_prob, obs_prob)
        prob_sum -= obs_prob
        max_prob_diagnose = max(diagnoses_with_prob + [max_prob_diagnose], key=operator.itemgetter(1))
        if max_prob_diagnose[1] >= prob_sum:
            return max_prob_diagnose
    return None

def diagnose(inputs, outputs, components):
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
        # consistent = all(outputs[name] == values[name] for name in outputs.keys())
        consistent = all(val == values[f'o{index+1}'] for index,val in enumerate(outputs))
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses
