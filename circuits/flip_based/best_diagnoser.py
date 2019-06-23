from circuits.utils.diagnoser_utils import *
from circuits.structures.trie import *
from circuits.utils import prob_utils


def find_best_diagnose(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    prob_sum = 1
    max_prob = 0
    max_prob_diagnoses = []
    for outputs, obs_prob in prob_utils.observation_lexicographic_iterator(orig_outputs, faulty_output_prob):
        diagnoses = diagnose(inputs, outputs, components, outputs_names)
        diagnoses_with_prob = calc_diagnoses_probs_given_obs_prob(diagnoses, faulty_comp_prob, obs_prob)
        prob_sum -= obs_prob
        max_prob_in_output = max(prob for diag,prob in diagnoses_with_prob)
        if max_prob_in_output >= max_prob:
            diags_with_max_prob = [(diag, prob) for diag,prob in diagnoses_with_prob if prob == max_prob_in_output]
            if max_prob_in_output == max_prob:
                max_prob_diagnoses += diags_with_max_prob
            else:
                max_prob = max_prob_in_output
                max_prob_diagnoses = diags_with_max_prob

        # max_prob_diagnose = max(diagnoses_with_prob + [max_prob_diagnose], key=operator.itemgetter(1))
        if max_prob >= prob_sum:
            return max_prob_diagnoses
    return None

def diagnose(inputs, outputs, components, outputs_names):
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
        consistent = all(outputs[i] == values[name] for i,name in enumerate(outputs_names))
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses
