from circuits.utils.diagnoser_utils import *
from circuits.utils.prob_utils import *
from circuits.structures.trie import *

def diagnose_all_combinations(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    diagnoses = {}
    ncomp = len(components)

    for suspected_diagnose in diagnoses_iterator(components):
        # propagate values in suspected diagnose
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

    all_diagnoses = []
    probs = []
    for outputs, (output_diags,_) in diagnoses.items():
        obs_prob = observation_flip_prob(orig_outputs, outputs, faulty_output_prob)
        all_diagnoses += output_diags
        probs += diags_prob(output_diags, faulty_comp_prob, ncomp, obs_prob)
        # diagnoses_with_prob += calc_diagnoses_probs_given_obs_prob(output_diags, faulty_comp_prob, obs_prob)
    sum_probs = sum(probs)
    return [(diag, prob / sum_probs) for diag, prob in zip(all_diagnoses, probs)]
