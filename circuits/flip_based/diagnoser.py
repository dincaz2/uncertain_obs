from circuits.utils.diagnoser_utils import *
from circuits.utils import prob_utils


def diagnose_all_combinations(inputs, orig_outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob):
    diagnoses = []
    probs = []
    ncomp = len(components)
    for outputs, obs_prob in prob_utils.observation_lexicographic_iterator(orig_outputs, faulty_output_prob):
        obs_diagnoses = diagnose_obs(inputs, outputs, components, outputs_names)
        diagnoses += obs_diagnoses
        probs += prob_utils.diags_prob(obs_diagnoses, faulty_comp_prob, ncomp, obs_prob)
        # diagnoses += calc_diagnoses_probs_given_obs_prob(obs_diagnoses, faulty_comp_prob, obs_prob)
    sum_probs = sum(probs)
    return [(diag, prob/sum_probs) for diag,prob in zip(diagnoses,probs)]