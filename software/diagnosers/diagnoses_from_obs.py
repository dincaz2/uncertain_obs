from software.utils import diagnoser_utils

def diagnose_all_combinations(inst, error, faulty_comp_prob, faulty_output_prob, uncertain_tests):
    diagnoses = {}

    for obs, obs_prob in diagnoser_utils.uncertain_observation_iterator(error, faulty_output_prob, uncertain_tests):
        # print(''.join(map(str, obs.values())) + str(obs_prob))
        diagnoser = inst(obs)
        if all(err==0 for err in obs.values()):
            diagnoses[tuple()] = obs_prob
            continue

        diagnoser.diagnose()
        for diag in diagnoser.diagnoses:
            comps = tuple(sorted(diag.diagnosis))
            old_diag_prob = diagnoses.get(comps, 0)
            diagnoses[comps] = old_diag_prob + diag.probability * obs_prob

    return diagnoses.items()