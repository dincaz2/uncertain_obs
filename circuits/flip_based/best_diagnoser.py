from circuits.utils.diagnoser_utils import *
from circuits.utils import prob_utils

def find_best_diagnoses(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    unseen_prob_sum = 1
    max_prob = 0
    max_prob_diagnoses = []
    ncomps = len(components)
    for outputs, obs_prob in prob_utils.observation_lexicographic_iterator(orig_outputs, faulty_output_prob):
        diagnoses = diagnose_obs(inputs, outputs, components, outputs_names)
        # diagnoses_with_prob = calc_diagnoses_probs_given_obs_prob(diagnoses, faulty_comp_prob, obs_prob)
        # unseen_prob_sum -= obs_prob
        # max_prob_in_output = max(prob for diag, prob in diagnoses_with_prob)
        probs = prob_utils.diags_prob(diagnoses, faulty_comp_prob, ncomps, obs_prob)
        unseen_prob_sum -= obs_prob
        # unseen_prob_sum -= sum(probs)
        max_prob_in_output = max(probs)
        if max_prob_in_output >= max_prob:
            diags_with_max_prob = [(diag, prob) for diag,prob in zip(diagnoses,probs) if prob == max_prob_in_output]
            if max_prob_in_output == max_prob:
                max_prob_diagnoses += diags_with_max_prob
            else:
                max_prob = max_prob_in_output
                max_prob_diagnoses = diags_with_max_prob

        # max_prob_diagnose = max(diagnoses_with_prob + [max_prob_diagnose], key=operator.itemgetter(1))
        if max_prob >= unseen_prob_sum:
            # print("MstLikeDiag - halt")
            return max_prob_diagnoses

    # print("MstLikeDiag - tried all")
    return max_prob_diagnoses