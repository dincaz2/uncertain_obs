import os
import re
import csv

__diagnosis_folder_path = r"output\black_box"
__output_folder_name = os.path.join(__diagnosis_folder_path, "output")
__diagnose_software_name2 = os.path.join(__diagnosis_folder_path, "SCryptoDiagnoser.exe")
__diagnose_software_name = os.path.join(__diagnosis_folder_path, "SCryptoDiagAll")
observations_path = os.path.join(__diagnosis_folder_path, "data")
csv_all = os.path.join(__diagnosis_folder_path, "{}_{}_all.csv")
csv_tld = os.path.join(__diagnosis_folder_path, "{}_{}_tld.csv")
__file_name_delimiter = "_"
__input_symbol = 'i'
__output_symbol = 'o'
__zero_symbol = '-'
__one_symbol = ''
__values_delimiter = ','
__observations_delimiter = '.'
data_set_type = "iscas85"
__tld_files_extension = ".tld"
__obs_files_extension = ".obs"

def diagnose(system_name, inputs, outputs, outputs_combinations):
    clean_directory(observations_path, __obs_files_extension)
    write_obs_to_file(system_name, inputs, outputs_combinations)
    # clean_directory(__output_folder_name, __tld_files)
    # os.system(f'{__diagnose_software_name} {system_name} {data_set_type}')

    time = calc_time_from_csv(system_name)
    return time


def calc_time_from_csv(system_name):
    time = 0

    skip = 4
    with open(csv_all.format(system_name, data_set_type)) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if skip:
                skip -= 1
                continue
            time += float(row[5])

    skip = 3
    with open(csv_tld.format(system_name, data_set_type)) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if skip:
                skip -= 1
                continue
            time += float(row[7])

    return time


def val2symbol(value, symbol, n):
    sym = '' if int(value) == 1 else __zero_symbol
    return f'{sym}{symbol}{n+1}'


def write_obs_to_file(system_name, inputs, outputs_list):
    file_name = os.path.join(observations_path, f'{system_name}_{data_set_type}{__obs_files_extension}')
    with open(file_name, 'w') as out:
        for index, outputs in enumerate(outputs_list):
            line = f'({system_name},{index+1},['
            input_symbols = [val2symbol(val, __input_symbol, i) for i,val in enumerate(inputs)]
            output_symbols = [val2symbol(val, __output_symbol, i) for i, val in enumerate(outputs)]
            line += ','.join(input_symbols) + ',' + ','.join(output_symbols) + ']).\n'
            out.write(line)


def clean_directory(path, with_extensin):
    for filename in os.listdir(path):
        if filename.endswith(with_extensin):
            os.remove(os.path.join(path, filename))