from circuits.utils.diagnoser_utils import *
from circuits.structures.trie import *

def diagnose_all_combinations(inputs, components, outputs_names, probs, faulty_comp_prob):
    diagnoses = {}

    for suspected_diagnose in diagnoses_iterator(components):
        # propogate values in suspected diagnose
        for comp in suspected_diagnose:
            comp.healthy = False
        values = inputs.copy()
        propogate_values(values, components)
        for comp in suspected_diagnose:
            comp.healthy = True

        # add to correct outputs combination if minimal-subset
        out_str = output_string(values, outputs_names)
        output_diagnoses, trie = diagnoses.setdefault(out_str, ([], make_trie()))
        if not check_trie_for_subsets(trie, suspected_diagnose):
            if any(set(suspected_diagnose).issuperset(set(s)) for s in output_diagnoses):
                print('\n---error---\n')
            output_diagnoses.append(suspected_diagnose)
            add_to_trie(trie, suspected_diagnose)
        elif not any(set(suspected_diagnose).issuperset(set(s)) for s in output_diagnoses):
            print('\n---error---2\n')

        # print(f'checked diagnose {[comp.name for comp in suspected_diagnose]}')

    return finalize({out_str:diagnose for out_str,(diagnose,_) in diagnoses.items()}, probs, outputs_names, faulty_comp_prob)
