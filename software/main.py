from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from time import time
from software.diagnosers import diagnoses_from_obs, best_obs, obs_from_diagnoses
import operator
import os
import csv
import numpy as np
from random import sample
from math import ceil

matrices_folder = 'matrices'
matrix_file_suffix = '.matrix'
results_folder_path = r"output\results"
faulty_comp_prob = 0.5
faulty_output_probs = [0.11, 0.09, 0.07, 0.05, 0.03, 0.01]

# inst = readPlanningFile("C:\\Users\\eyalhad\\Desktop\\SFL-diagnoser\\MatrixFile2.txt")
# inst.diagnose()
# results = Diagnosis_Results(inst.diagnoses, inst.initial_tests, inst.error)
# results.get_metrics_names()
# results.get_metrics_values()
# ei = software.sfl_diagnoser.Diagnoser.ExperimentInstance.addTests(inst, inst.hp_next_by_prob())
# i=5

def file2tuple(file):
    ncomps,ntests,nfailed,sample = list(map(int, file.split('.')[0].split('_')))
    ncomps = ncomps + 100 if sample>10 else ncomps
    return ncomps,ntests,nfailed,sample

def find_matrix_index(matrices, matrix):
    return dict(reversed(enumerate(matrices)))[matrix]

def pipeline(folder, output):
    # matrices = [a for a in
    #             ['0aa57f04ede369a4f813bbb86d3eac1ed20b084c.matrix2', '0cc451d5e5cb565eb7311308466f487bc534ebaf.matrix2',
    #              '19f33e4e0d824e732d07f06a08567c27b3c808f3.matrix2', '1c606c3d96838e595a0664cbafdd60caae34aa0e.matrix2',
    #              '229151ec41339450e4d4f857bf92ed080d3e2430.matrix', '3905071819a14403d1cdb9437d2e005adf18fc70.matrix',
    #              '3b46d611b2d595131ce0bce9bdb3209c55391be7.matrix', '3cea4b2af3f9caf6aa72fa56d647c513d320e073.matrix',
    #              '3f900a7395e31eaa72e0fa2fb43c090e5a8fa4ed.matrix', '48bf241d4149919e0928e39616bee2e3783e2987.matrix',
    #              '5209cefa81c9c48a34e5472fdcf2a308a4da2589.matrix', '575be16474e8e8246d4bbde6f243fdf38c34ad5b.matrix',
    #              '68217617c54467c7c6098168e714a2fb6a48847d.matrix', '8da5fb28a764eee26c76a5018c293f224017887b.matrix',
    #              'ac2a39e92a71d5f9eb3ca7c6cc789b6341c582a4.matrix', 'ac58807ede6d9a0625b489cdca6fd37bad9cacfe.matrix',
    #              'b2f1757bf9ec1632a940b9a2e65a1a022ba54af8.matrix', 'b5906d3f325ca3a1147d5fa68912975e2e6c347e.matrix',
    #              'b6f7a8a8be57c9525c59e9f21e958e76cee0dbaf.matrix', 'cbf8e4eb017a99af9a8f24eb8429e8a12b62af8b.matrix',
    #              'cf28c89dcf72d27573c478eb91e3b470de060edd.matrix', 'cfff06bead88e2c1bb164285f89503a919e0e27f.matrix',
    #              'e28c95ac2ce95852add84bdf3d2d9c00ac98f5de.matrix', 'ec0c4e5508dbd8af83253f7c50f8b728a1003388.matrix',
    #              'temp.matrix'] if a.endswith(matrix_file_suffix)]
    # matrices = ['temp.matrix']
    matrices = [file for file in os.listdir(folder) if file.endswith(matrix_file_suffix)]
    matrices = sorted(matrices, key=file2tuple) # for logic traversal of matrices. also taking only 10 samples instead of 20
    print(f'total of {len(matrices)} matrices')
    last_crash = '14_14_2_6.matrix'
    from_index = dict(map(reversed,enumerate(matrices)))[last_crash]
    matrices = matrices[from_index:]
    print(f'remaining {len(matrices)} matrices')
    # print(matrices[0])
    # return
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('matrix_name', '#components', '#tests', '#failing_tests', '#uncertain_tests', 'faulty_output_prob', 'error_vector',
                         'scan_all_obs_time', 'scan_all_diags_time', 'scan_best_obs_time',
                         'scan_all_obs_best_cardinality', 'scan_all_diags_best_cardinality', 'scan_best_obs_best_cardinality',
                         'scan_all_obs_mean_cardinality', 'scan_all_diags_mean_cardinality', 'scan_best_obs_mean_cardinality',
                         'scan_all_obs_output', 'scan_all_diags_output', 'scan_best_obs_output'))
        f.flush()
        for matrix_file in matrices:
            # if int(matrix_file.split('.')[0].split('_')[3]) > 10:
            #     print(f'skipping matrix {matrix_file}')
            #     continue
            print(f'diagnosing matrix {matrix_file}')

            inst, error, initials = readPlanningFile(os.path.join(folder, matrix_file))
            error_vec = list(map(operator.itemgetter(1), sorted(error.items(), key=operator.itemgetter(0))))
            num_of_comps = len(Experiment_Data().COMPONENTS_NAMES.keys())
            all_tests = Experiment_Data().POOL.keys()
            num_of_tests = len(all_tests)
            num_failing_tests = error_vec.count(1)
            print(f'comps: {num_of_comps}, tests: {num_of_tests}, failing: {num_failing_tests}')

            for proportion_uncertain in [0.1, 0.3, 0.5, 0.7, 1]:
                num_uncertain = ceil(num_of_tests * proportion_uncertain)
                uncertain_tests = sample(all_tests, num_uncertain)
                # print(f'time: {time()}')
                print(f'uncertain tests: {uncertain_tests}')

                alg1_result, alg1_time, alg1_best_diag_card, alg1_mean_card = run_diagnoser(inst, error, faulty_output_probs[0], uncertain_tests)
                print(f'\tdiags from obs: {alg1_time} seconds')
                print(f'\t\t{alg1_result}')

                alg2_result, alg2_time, alg2_best_diag_card, alg2_mean_card = run_obs_from_diagnoses(error, initials, faulty_output_probs[0], uncertain_tests)
                print(f'\tobs from diags: {alg2_time} seconds')
                print(f'\t\t{alg2_result}')

                for faulty_output_prob in faulty_output_probs:
                    alg3_result, alg3_time, alg3_best_diag_card, alg3_mean_card = run_best_diagnoser(inst, error, faulty_output_prob, uncertain_tests)
                    print(f'\tbest obs with faulty output prob of {faulty_output_prob}: {alg3_time} seconds')
                    print(f'\t\t{alg3_result}')
                    writer.writerow((matrix_file, num_of_comps, num_of_tests, num_failing_tests, num_uncertain, faulty_output_prob, error_vec,
                                     alg1_time, alg2_time, alg3_time,
                                     alg1_best_diag_card, alg2_best_diag_card, alg3_best_diag_card,
                                     alg1_mean_card, alg2_mean_card, alg3_mean_card,
                                     alg1_result, alg2_result, alg3_result))
                    f.flush()
                print()
            print('\n\n\n')


def diagnoser(func):
    def func_wrapper(*args, **kwargs):
        start = time()
        diagnoses = func(*args, **kwargs)
        end = time()
        diagnoses = [(diagnose, round(prob, 6)) for diagnose, prob in diagnoses]
        diagnoses = sorted(diagnoses, key=operator.itemgetter(1, 0), reverse=True)
        top_diagnoses = diagnoses[:10]
        best_diag_cardinality = len(diagnoses[0][0])
        mean_cardinality = np.mean([len(d[0]) for d in diagnoses])

        p = sum(map(operator.itemgetter(1), diagnoses))
        print(f"sum of probs: {p}")
        return top_diagnoses, end - start, best_diag_cardinality, mean_cardinality
    return func_wrapper

@diagnoser
def run_diagnoser(inst, error, faulty_output_prob, uncertain_tests):
    return diagnoses_from_obs.diagnose_all_combinations(inst, error, faulty_comp_prob, faulty_output_prob, uncertain_tests)

@diagnoser
def run_best_diagnoser(inst, error, faulty_output_prob, uncertain_tests):
    return best_obs.find_best_diagnoses(inst, error, faulty_comp_prob, faulty_output_prob, uncertain_tests)

@diagnoser
def run_obs_from_diagnoses(error, initials, faulty_output_prob, uncertain_tests):
    return obs_from_diagnoses.diagnose_all_combinations(error, initials, faulty_comp_prob, faulty_output_prob, uncertain_tests)


if __name__ == '__main__':
    # name = 'real'
    name = 'synthetic'
    folder = os.path.join(matrices_folder, name)
    output = os.path.join(results_folder_path, f'matrices_{name}.csv')
    pipeline(folder, output)
    # from software.utils.matrix_generator import generate_all
    # generate_all()