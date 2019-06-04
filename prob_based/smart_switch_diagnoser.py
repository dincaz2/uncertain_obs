from utils.diagnoser_utils import *
from structures.trie import *
from utils import prob_utils


def diagnose_all_combinations(inputs, components, outputs_names, probs, faulty_comp_prob):
    diagnoses_dict = {}
    sorted_combinations = prob_utils.observations_iterator(probs)
    components_outputs_dict = outputs2comps(components)

    # first diagnose
    outputs = next(sorted_combinations)
    diagnoses = diagnose(inputs, outputs, components, components, [[]])
    out_str = output_string(outputs, outputs_names)
    diagnoses_dict[out_str] = diagnoses
    old_diagnoses = diagnoses
    old_outputs = outputs

    for outputs in sorted_combinations:
        sub_comps = collect_touching_components(old_outputs, outputs, components_outputs_dict) # collect all components which can affect any changed output between the combinations
        sub_diagnoses = [list(set(diag).difference(sub_comps)) for diag in old_diagnoses] # remove touching components from old diagnoses
        diagnoses = diagnose(inputs, outputs, components, list(sub_comps), sub_diagnoses)
        out_str = output_string(outputs, outputs_names)
        diagnoses_dict[out_str] = diagnoses
        old_diagnoses = diagnoses
        old_outputs = outputs
    return finalize(diagnoses_dict, probs, outputs_names, faulty_comp_prob)

def diagnose(inputs, outputs, all_components, suspected_components, initial_diagnoses):
    # print(f'\ndiagnosing outputs {outputs}')
    diagnoses = []
    diagnoses_trie = make_trie()

    queue = deque([(diag, -1) for diag in initial_diagnoses])
    length = len(all_components)
    while queue:
        suspected_diagnose, max_in_subset = queue.popleft()
        if check_trie_for_subsets(diagnoses_trie, suspected_diagnose):
            continue
        # print(f'checking diagnose {[comp.name for comp in suspected_diagnose]}')

        for comp in suspected_diagnose:
            comp.healthy = False
        values = inputs.copy()
        propogate_values(values, all_components)
        for comp in suspected_diagnose:
            comp.healthy = True

        # check consistency
        consistent = all(outputs[name] == values[name] for name in outputs.keys())
        if consistent:
            diagnoses.append(suspected_diagnose)
            add_to_trie(diagnoses_trie, suspected_diagnose)
        elif max_in_subset < length - 1:
            for index, comp in enumerate(suspected_components[max_in_subset + 1:]):
                queue.append((suspected_diagnose + [comp], index + max_in_subset + 1))
    return diagnoses

def collect_touching_components(old_outputs, outputs, components_outputs_dict):
    comps = set()
    for output in get_changed_outputs(old_outputs, outputs):
        comps.update(components_outputs_dict[output])
    return comps

def get_changed_outputs(old_outputs, new_outputs):
    outputs = []
    for output_name, old_output_val in old_outputs.items():
        if old_output_val != new_outputs[output_name]:
            outputs.append(output_name)
    return outputs

def all_components_outputs(components):
    components2outputs_dict = {} # {component_name : outputs_affected_by_comp}
    fan_out = {} # {port_name : [components_have_this_port_as_input]}

    for comp in components[::-1]: # traverse components in reverse order to compute outputs
        if comp.output[0] == 'o':
            components2outputs_dict[comp] = {comp.output}
        else:
            outputs = set()
            for fan_out_comp in fan_out[comp.output]:
                outputs.update(components2outputs_dict[fan_out_comp])
            components2outputs_dict[comp] = outputs
        for input in comp.inputs:
            fan_outs = fan_out.setdefault(input, [])
            fan_outs.append(comp)
    return components2outputs_dict

def outputs2comps(components):
    output2comps_dict = {} # {output : comps_touching_this_output}
    comp2outputs_dict = all_components_outputs(components)

    for comp, outputs in comp2outputs_dict.items():
        for output in outputs:
            comps = output2comps_dict.setdefault(output, [])
            comps.append(comp)
    return output2comps_dict