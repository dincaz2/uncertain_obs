from datetime import datetime
import os
from software import real_diagnoser, synthetic_diagnoser, reduction_checker

matrices_folder = 'matrices'
results_folder_path = r"output\results"

if __name__ == '__main__':
    # name = 'real'
    name = 'synthetic'
    reduction = False

    date = datetime.now().strftime("%d-%m-%Y")
    diagnoser = real_diagnoser if name == 'real' else (reduction_checker if reduction else synthetic_diagnoser)
    folder = os.path.join(matrices_folder, name)
    output = os.path.join(results_folder_path, f'matrices_{name}_{date}.csv')

    diagnoser.pipeline(folder, output)
    # from software.utils.matrix_generator import generate_all
    # generate_all()