from utils.diagnoser_utils import *
from structures.trie import *
from utils import prob_utils


def diagnose_all_combinations(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    diagnoses = []
    for outputs, obs_prob in prob_utils.observation_lexicographic_iterator(orig_outputs, faulty_output_prob):
        obs_diagnoses = diagnose(inputs, outputs, components, outputs_names)
        diagnoses += calc_diagnoses_probs_given_obs_prob(obs_diagnoses, faulty_comp_prob, obs_prob)
    return diagnoses

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
        consistent = all(outputs[i] == values[name] for i,name in enumerate(outputs_names))
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses
