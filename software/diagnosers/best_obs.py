from software.utils import diagnoser_utils

def find_best_diagnoses(inst, error, faulty_comp_prob, faulty_output_prob, uncertain_tests):
    diagnoses = {}
    unseen_prob_sum = 1

    for obs, obs_prob in diagnoser_utils.uncertain_observation_iterator(error, faulty_output_prob, uncertain_tests):
        diagnoser = inst(obs)
        if all(err==0 for err in obs.values()):
            diagnoses[tuple()] = obs_prob
        else:
            diagnoser.diagnose()
            for diag in diagnoser.diagnoses:
                comps = tuple(sorted(diag.diagnosis))
                old_diag_prob = diagnoses.get(comps, 0)
                diagnoses[comps] = old_diag_prob + diag.probability * obs_prob

        unseen_prob_sum -= obs_prob
        max_prob = max(diagnoses.values())
        second_max_prob = max(list(filter(lambda p: p < max_prob, diagnoses.values())) + [0])
        if max_prob - second_max_prob > unseen_prob_sum:
            return [(d,p) for d,p in diagnoses.items() if p == max_prob]

    return [(d,p) for d,p in diagnoses.items() if p == max(diagnoses.values())]