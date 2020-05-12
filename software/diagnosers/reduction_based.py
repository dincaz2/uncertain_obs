from software.utils import diagnoser_utils
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data

def diagnose_all_combinations(inst, error, faulty_output_prob, uncertain_tests):
    components_dict = Experiment_Data().COMPONENTS_NAMES
    # sum_probs = diagnoser_utils.obs_normalization(len(uncertain_tests), faulty_output_prob)
    diagnoses = {}
    diagnoser = inst(error)
    diagnoser.diagnose()
    for diag in diagnoser.diagnoses:
        comps = sorted([components_dict[c] for c in diag.diagnosis])
        filtered_comps = tuple(comp for comp in comps if comp.startswith('c'))
        # num_of_test_in_diag = len(comps) - len(filtered_comps)
        # obs_prob =  pow(faulty_output_prob,num_of_test_in_diag) / sum_probs
        old_diag_prob = diagnoses.get(filtered_comps, 0)
        diagnoses[filtered_comps] = old_diag_prob + diag.probability

    return diagnoses.items()