import os
from circuits.utils import obs_parser as bfs_obs_parser, model_parser as bfs_model_parser
from circuits.prob_based import obs_from_diagnoses as bfs_obs_from_diagnoses, diagnoser as bfs_diagnoser, \
    best_diagnoser as best_diagnoser
from circuits.flip_based import best_diagnoser as noise_best_diagnoser
from circuits.flip_based import diagnoser as noise_diagnoser
from circuits.flip_based import obs_from_diagnoses as noise_obs_from_diagnoses
import operator
from time import time
import csv
import random

observations_input_path = r"input\Data_iscas85"
systems_input_path = r"input\Data_Systems"
diagnosis_folder_path = r"output\black_box"
diagnosis_output_path = r"output\black_box\output"
summary_folder_path = r"output"
results_folder_path = r"output\results"
faulty_comp_prob = 0.1
faulty_output_probs = [0.11, 0.09, 0.07, 0.05, 0.03, 0.01]


def pipeline():
    # system_names = ['c17', '74182', '74283', '74181', 'c432', 'c880', 'c3540', 'c1908']
    system_names = ['c17', '74182']
    system_names = ['c17']
    file_template = os.path.join(results_folder_path, '{}.csv')
    for system_name in system_names:
        print(f'diagnosing system {system_name}')
        filename = file_template.format(system_name)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(('inputs', 'outputs', 'faulty_output_prob',
                             'regular_diagnoser_time', 'backward_diagnoser_time', 'best_prob_diagnoser_time',
                             'regular_diagnoser_output', 'backward_diagnoser_output', 'best_prob_diagnoser_output'))
            f.flush()
            inputs_system, outputs_system, components = bfs_model_parser.parse_file(
                os.path.join(systems_input_path, f'{system_name}.sys'))

            print('observation ', end='')
            for index, (inputs, outputs) in enumerate(bfs_obs_parser.parse_all_obs(os.path.join(observations_input_path, f'{system_name}_iscas85.obs'))):
                print(f'#{index+1} ', end='')
                if set(inputs_system) != set(inputs.keys()) or set(outputs_system) != set(outputs.keys()):
                    print("Mismatch between system inputs\outputs names and observarion inputs\outputs names")
                    return
                # print(f'observation inputs: {inputs}')
                # print(f'observation outputs: {outputs}')
                outputs = [outputs[f'o{index+1}'] for index in range(len(outputs))]
                inputs_vector = [inputs[f'i{index+1}'] for index in range(len(inputs))]

                alg1_result, alg1_time = run_diagnoser(inputs, outputs, components, outputs_system, faulty_output_probs[0])
                alg2_result, alg2_time = run_obs_from_diagnoses(inputs, outputs, components, outputs_system, faulty_output_probs[0])
                for faulty_output_prob in faulty_output_probs:
                    alg3_result, alg3_time = run_noise_best_diagnoser(inputs, outputs, components, outputs_system, faulty_output_prob)
                    writer.writerow((inputs_vector, outputs, faulty_output_prob,
                                     alg1_time, alg2_time, alg3_time, alg1_result, alg2_result, alg3_result))
                    f.flush()
            print()

def diagnoser(func):
    def func_wrapper(*args, **kwargs):
        start = time()
        diagnoses = func(*args, **kwargs)
        end = time()
        diagnoses = [(diagnose, round(prob, 6)) for diagnose, prob in diagnoses]
        diagnoses = sorted(diagnoses, key=operator.itemgetter(1, 0), reverse=True)
        max_diags = [(diag, prob) for diag, prob in diagnoses if prob == diagnoses[0][1]]
        # p = sum(map(operator.itemgetter(1), diagnoses))
        # print(f"sum of probs: {p}")
        return max_diags, end - start
    return func_wrapper

@diagnoser
def run_noise_best_diagnoser(inputs, outputs, components, outputs_names, faulty_output_prob):
    return noise_best_diagnoser.find_best_diagnoses(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)

@diagnoser
def run_obs_from_diagnoses(inputs, outputs, components, outputs_names, faulty_output_prob):
    return noise_obs_from_diagnoses.diagnose_all_combinations(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)

@diagnoser
def run_diagnoser(inputs, outputs, components, outputs_names, faulty_output_prob):
    return noise_diagnoser.diagnose_all_combinations(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)

if __name__ == '__main__':
    pipeline()