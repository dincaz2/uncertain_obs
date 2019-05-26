"""
A class that receives a folder path, goes through the different files and separates observations.
It outputs a dictionary of system name in the key and observations in the value.

"""
import os.path  # enables operating system dependant functions, useful for traversing through files and directories
import random
from enum import Enum

__weight_binary = 0.5
__minimal_prob_range = 0.8
__digits_after_the_dot = 3
__input_symbol = 'i'
__output_symbol = 'o'
__zero_symbol = '-'
__one_symbol = ''
__values_delimiter = ','
__observations_delimiter = '.'

def parse_file(obs_path, index_in_file):
    """
    The ".obs" file need to be in this format:
    (<system id>,<observations set>,[<observation id>]).
    For example:
    (c17,1,[-i1,i2,i3,-i4,-i5,-o1,-o2]).
    (c17,2,[-i1,i2,-i3,i4,i5,o1,-o2]).
    In the example above, observation that start with 'i' is to input and 'o' is to output.
    observation that start with '-' is equal to 0 and without '-' is equal to 1.
    :param obs_path: observation file path
    :param combination_mode: ALL for all combination, HIGH for most of them
    :param index_in_file: index of the observation in the file
    :return: system name
    """

    with open(obs_path) as f:
        file_content = f.read()
    inputs, outputs = parse(file_content, index_in_file)

    outputs = create_output_probability(outputs)
    # final_observation_dictionary = create_all_combinations()

    # ___write_to_files(final_observation_dictionary, observations_output_path, data_set_type)

    return inputs, outputs#, create_all_combinations(outputs.keys())


def parse(file_content, index_in_file):
    try:
        obs_string = file_content.split(__observations_delimiter)[index_in_file]
    except:
        return None
    obs_string = obs_string.replace('\n', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    values_list = obs_string.split(__values_delimiter)

    system_name = values_list[0]
    inputs, outputs = obs_format_to_binary(values_list[2:])

    return inputs, outputs


def obs_format_to_binary(value_list):
    input_dic = {}
    output_dic = {}
    for item in value_list:
        if item:
            item, item_value = (item[1:], 0) if item[0] == __zero_symbol else (item, 1)
            if item[0] == __input_symbol:
                input_dic[item] = item_value
            elif item[0] == __output_symbol:
                output_dic[item] = item_value

    return input_dic, output_dic


def create_output_probability(output):
    """
    This function randomizes a probability for zero for each output
    """
    return {out: round(random.uniform(0, 1), __digits_after_the_dot) for out,val in output.items()}


def create_all_combinations(output):
    """
    This function creates all 2^|output| combinations of outputs
    """
    # This format function transforms an integer to its binary representatin with a padding of |output| zeroes
    size = len(output)
    return [dict(zip(output, [int(x) for x in format(i, f'0{size}b')])) for i in range(1 << size)]
