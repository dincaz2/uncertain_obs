
from software.utils import diagnoser_utils
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data

def diagnose_all_combinations(inst, error, faulty_comp_prob, faulty_output_prob, uncertain_tests):
    components_dict = Experiment_Data().COMPONENTS_NAMES
    diagnoses = {}

    for obs, obs_prob in diagnoser_utils.uncertain_observation_iterator(error, faulty_output_prob, uncertain_tests):
        # print(''.join(map(str, obs.values())) + str(obs_prob))
        diagnoser = inst(obs)
        if all(err==0 for err in obs.values()):
            diagnoses[tuple()] = obs_prob
            continue

        diagnoser.diagnose(normalize=False)
        for diag in diagnoser.diagnoses:
            comps = tuple(sorted([components_dict[c] for c in diag.diagnosis]))
            # comps = tuple(sorted(diag.diagnosis))
            old_diag_prob = diagnoses.get(comps, 0)
            diagnoses[comps] = old_diag_prob + diag.probability * obs_prob

    diagnoses_with_probs = diagnoses.items()
    sum_probs = sum(prob for _,prob in diagnoses_with_probs)
    return [(diag, prob/sum_probs) for diag,prob in diagnoses_with_probs]

def diagnose_smart_mhs(diagnoser, faulty_comp_prob, faulty_output_prob):
    components_dict = Experiment_Data().COMPONENTS_NAMES
    diagnoses = {}
    for obs_diags, obs_prob in diagnoser.diagnose(faulty_comp_prob, faulty_output_prob, normalize=False):
        for diag in obs_diags:
            comps = tuple(sorted([components_dict[c] for c in diag.diagnosis]))
            diagnoses[comps] = diagnoses.get(comps, 0) + diag.probability * obs_prob

    sum_probs = sum(diagnoses.values())
    return [(diag, prob / sum_probs) for diag, prob in diagnoses.items()]