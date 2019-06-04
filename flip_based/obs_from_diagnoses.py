from utils.diagnoser_utils import *
from utils.prob_utils import *
from structures.trie import *

def diagnose_all_combinations(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    diagnoses = {}

    for suspected_diagnose in diagnoses_iterator(components):
        # propogate values in suspected diagnose
        for comp in suspected_diagnose:
            comp.healthy = False
        values = inputs.copy()
        propogate_values(values, components)
        for comp in suspected_diagnose:
            comp.healthy = True

        # add to correct outputs combination if minimal-subset
        out_tup = output_tuple(values, outputs_names)
        output_diagnoses, trie = diagnoses.setdefault(out_tup, ([], make_trie()))
        if not check_trie_for_subsets(trie, suspected_diagnose):
            output_diagnoses.append(suspected_diagnose)
            add_to_trie(trie, suspected_diagnose)

        # print(f'checked diagnose {[comp.name for comp in suspected_diagnose]}')

    diagnoses_with_prob = []
    for outputs, (output_diags,_) in diagnoses.items():
        obs_prob = observation_flip_prob(orig_outputs, outputs, faulty_output_prob)
        diagnoses_with_prob += calc_diagnoses_probs_given_obs_prob(output_diags, faulty_comp_prob, obs_prob)
    return diagnoses_with_prob
