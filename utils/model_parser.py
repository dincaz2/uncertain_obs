from structures.gate import Gate

def parse_file(model_path):
    with open(model_path) as f:
        file_content = f.read()
    name_arg, inputs, outputs, gates_arg, _ = file_content.split('.')
    inputs = clean_line(inputs).split(',')
    outputs = clean_line(outputs).split(',')
    gates = []
    for line in gates_arg.split('\n'):
        if not line:
            continue
        gate_desc = clean_line(line).split(',')
        if not gate_desc[-1]:
            gate_desc = gate_desc[:-1]
        gates.append(Gate(gate_desc[0], gate_desc[1], gate_desc[2], gate_desc[3:]))
    return inputs, outputs, gates


def clean_line(line):
    return line.replace('[','').replace(']','').replace('[','').replace('\n','').strip()