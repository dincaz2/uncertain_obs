from datetime import datetime
import os
from software import real_diagnoser, synthetic_diagnoser, reduction_checker, smart_mhs_diagnoser

matrices_folder = 'matrices'
results_folder_path = r"output\results"

def main():
	# os.chdir("software")

	# name = 'real'
	# name = 'synthetic'
	# name = 'reduction'
	name = 'smart_mhs'

	date = datetime.now().strftime("%d-%m-%Y")
	diag_dict = {'real': real_diagnoser, 'synthetic': synthetic_diagnoser, 'reduction': reduction_checker, 'smart_mhs': smart_mhs_diagnoser}
	diagnoser = diag_dict[name]
	# diagnoser = real_diagnoser if name == 'real' else (reduction_checker if reduction else synthetic_diagnoser)
	folder = os.path.join(matrices_folder, 'real' if name == 'real' else 'synthetic')

	output = os.path.join(results_folder_path, f'matrices_{name}_{date}.csv')

	diagnoser.pipeline(folder, output)
    # from software.utils.matrix_generator import generate_all
    # generate_all()

if __name__ == '__main__':
    main()