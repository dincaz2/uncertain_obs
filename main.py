import os
from prob_based import best_diagnoser as best_diagnoser
from utils import model_parser as bfs_model_parser, obs_parser as bfs_obs_parser
from prob_based import diagnoser as bfs_diagnoser
from prob_based import obs_from_diagnoses as bfs_obs_from_diagnoses
from flip_based import best_diagnoser as noise_best_diagnoser
from flip_based import diagnoser as noise_diagnoser
from flip_based import obs_from_diagnoses as noise_obs_from_diagnoses
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
faulty_comp_prob = 0.5
faulty_output_probs = [0.11, 0.09, 0.07, 0.05, 0.03, 0.01]


def foo():
    to_sort = [(['gate11'], 0.31684), (['gate16'], 0.31684), (['gate22', 'gate23'], 0.15842), (['gate23'], 0.032633), (['gate22'], 0.032633),
     (['gate10', 'gate11'], 0.016317), (['gate10', 'gate16'], 0.016317), (['gate11', 'gate22'], 0.016317),
     (['gate16', 'gate22'], 0.016317), (['gate11', 'gate19'], 0.016317), (['gate11', 'gate23'], 0.016317),
     (['gate16', 'gate19'], 0.016317), (['gate16', 'gate23'], 0.016317), ([], 0.0121)]
    random.shuffle(to_sort)
    print(f'shuffled: {to_sort}')
    after = sorted(to_sort, key=operator.itemgetter(1,0), reverse=True)
    print(f'sorted: {after}')


def pipeline():
    # system_names = ['c17', '74182', '74283', '74181', 'c432', 'c880', 'c3540', 'c1908']
    system_names = ['c17', '74182']
    file_template = r'output\results\{}.csv'
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

def run_noise_best_diagnoser(inputs, outputs, components, outputs_names, faulty_output_prob):
    start = time()
    best_diagnoses = noise_best_diagnoser.find_best_diagnose(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)
    end = time()
    # print(f'with noise: best diagnose found in {end - start} seconds')
    best_diagnoses = sorted(best_diagnoses, key=operator.itemgetter(0), reverse=True)
    # print(best_diagnose)
    return best_diagnoses, end - start


def run_obs_from_diagnoses(inputs, outputs, components, outputs_names, faulty_output_prob):
    start = time()
    diag2obs = noise_obs_from_diagnoses.diagnose_all_combinations(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)
    end = time()
    # print(f'obs from diags: {end - start} seconds')
    diag2obs = sorted(diag2obs, key=operator.itemgetter(1,0), reverse=True)
    max_diags = [(diag, prob) for diag,prob in diag2obs if prob == diag2obs[0][1]]
    # print(diag2obs)
    return max_diags, end - start


def run_diagnoser(inputs, outputs, components, outputs_names, faulty_output_prob):
    start = time()
    obs2diags = noise_diagnoser.diagnose_all_combinations(inputs, outputs, components, outputs_names, faulty_comp_prob, faulty_output_prob)
    end = time()
    # print(f'diags from obs: {end - start} seconds')
    obs2diags = sorted(obs2diags, key=operator.itemgetter(1,0), reverse=True)
    max_diags = [(diag, prob) for diag, prob in obs2diags if prob == obs2diags[0][1]]
    # print(obs2diags)
    return max_diags, end - start


def pipeline2():
    # system_names = ['74181', '74182', '74283', 'c1355', 'c17', 'c1908', 'c2670', 'c3540', 'c432', 'c499', 'c5315', 'c6288', 'c7552', 'c880']
    system_names = ['c17', '74182', '74283', '74181', 'c432', 'c880', 'c3540', 'c1908']
    # system_names = ['c17', '74182']
    for system_name in system_names:
        inputs_system, outputs_system, components = bfs_model_parser.parse_file(os.path.join(systems_input_path, f'{system_name}.sys'))
        inputs, outputs_probs = bfs_obs_parser.parse_file(os.path.join(observations_input_path, f'{system_name}_iscas85.obs'), 0)
        if set(inputs_system) != set(inputs.keys()) or set(outputs_system) != set(outputs_probs.keys()):
            print("Mismatch between system inputs\outputs names and observarion inputs\outputs names")
            return
        print(f'diagnosing system {system_name}')
        print(f'observation inputs: {inputs}')
        # outputs_probs = {'o1': 0.187, 'o2': 0.8, 'o3': 0.185, 'o4': 0.173, 'o5': 0.493} # TODO: delete
        # outputs_probs = {'o1': 0.134, 'o2': 0.432} # TODO: delete
        print(f'observation outputs probability for zero: {outputs_probs}')

        # start = time()
        # smart_switch_diags = bfs_smart_switch_diagnoser.diagnose_all_combinations(inputs, components, outputs_system, outputs_probs, faulty_comp_prob)
        # end = time()
        # print(f'smart switch diagnoser: {end - start} seconds. Not working unfortunately')
        # print(sorted(smart_switch_diags, key=operator.itemgetter(1), reverse=True))

        start = time()
        best_diagnose = noise_best_diagnoser.find_best_diagnose(inputs, components, outputs_system, faulty_comp_prob, 0.02)
        end = time()
        print(f'with noise: best diagnose found in {end - start} seconds')
        print(best_diagnose)

        start = time()
        best_diagnose = best_diagnoser.find_best_diagnose(inputs, components, outputs_system, outputs_probs, faulty_comp_prob)
        end = time()
        print(f'best diagnose found in {end - start} seconds')
        print(best_diagnose)

        start = time()
        diag2obs = bfs_obs_from_diagnoses.diagnose_all_combinations(inputs, components, outputs_system, outputs_probs, faulty_comp_prob)
        end = time()
        print(f'obs from diags: {end - start} seconds')
        print(sorted(diag2obs, key=operator.itemgetter(1), reverse=True))

        start = time()
        obs2diags = bfs_diagnoser.diagnose_all_combinations(inputs, components, outputs_system, outputs_probs, faulty_comp_prob)
        end = time()
        print(f'diags from obs: {end - start} seconds')
        print(sorted(obs2diags, key=operator.itemgetter(1), reverse=True))

        print()


if __name__ == '__main__':
    pipeline()