from utils.diagnoser_utils import *
from structures.trie import *
from utils import prob_utils


def diagnose_all_combinations(inputs, components, outputs_names, probs, faulty_comp_prob):
    diagnoses_dict = {}
    for outputs in prob_utils.observations_iterator(probs):
        diagnoses = diagnose(inputs, outputs, components)
        out_str = output_string(outputs, outputs_names)
        diagnoses_dict[out_str] = diagnoses
    return finalize(diagnoses_dict, probs, outputs_names, faulty_comp_prob)

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
        consistent = all(outputs[name] == values[name] for name in outputs.keys())
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses
