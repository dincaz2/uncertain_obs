import os
from bfs_diagnose import obs_parser as bfs_obs_parser
from bfs_diagnose import model_parser as bfs_model_parser
from bfs_diagnose import diagnoser as bfs_diagnoser
from bfs_diagnose import smart_switch_diagnoser as bfs_smart_switch_diagnoser
from bfs_diagnose import obs_from_diagnoses as bfs_obs_from_diagnoses
from best_diagnose import diagnoser as best_diagnoser
from best_diagnose import noise_diagnoser as noise_best_diagnoser
from sat_solver_diagnose.satbd_diagnoser import diagnose
import operator
from time import time
from best_diagnose import prob_utils

observations_input_path = r"input\Data_iscas85"
systems_input_path = r"input\Data_Systems"
diagnosis_folder_path = r"output\black_box"
diagnosis_output_path = r"output\black_box\output"
summary_folder_path = r"output"
faulty_comp_prob = 0.5

def pipeline():
    # system_names = ['74181', '74182', '74283', 'c1355', 'c17', 'c1908', 'c2670', 'c3540', 'c432', 'c499', 'c5315', 'c6288', 'c7552', 'c880']
    system_names = ['c17', '74182', '74183', '74281', 'c432', 'c880', 'c3540', 'c1908']
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