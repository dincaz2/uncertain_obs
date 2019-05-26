from fibonacci_heap_mod import Fibonacci_heap
import operator
import random
from collections import deque
import scipy.special as sc

def observations_iterator(probs):
    # yield first obs with all outputs probs > 0.5
    max_obs = {name: (0,p) if p > 0.5 else (1,1-p) for name,p in probs.items()}
    sorted_outputs = sorted(max_obs.items(), key=lambda x: x[1][1])
    output_names, pack = zip(*sorted_outputs)
    max_obs_values, output_probs = zip(*pack)
    yield dict(zip(output_names, max_obs_values))

    size = len(output_names) - 1
    heap = Fibonacci_heap()
    values = list(max_obs_values)
    max_index = 0
    values[max_index] = 1 - values[max_index]
    prob = observation_prob(dict(zip(output_names, values)), probs)
    heap.enqueue((values, max_index, prob, None), -prob)
    while len(heap) > 0:
        values, max_index, prob, next_node = heap.dequeue_min().m_elem
        if next_node:
            heap.enqueue(next_node, -next_node[2])
        yield dict(zip(output_names, values))
        if max_index == size:
            continue

        # add left child - switch max index key i with i+1 : update values and probability
        # create right child for later - add i+1 key
        values_right_node = values[:]
        max_index_right_node = max_index + 1
        values_right_node[max_index_right_node] = 1 - values_right_node[max_index_right_node]
        prob_right_node = prob * ((1 / output_probs[max_index_right_node]) - 1)
        right_node = (values_right_node, max_index_right_node, prob_right_node, None)

        values_left_node = values_right_node[:]
        values_left_node[max_index] = 1 - values_left_node[max_index]
        prob_left_node = prob_right_node / ((1/output_probs[max_index]) - 1)

        heap.enqueue((values_left_node, max_index + 1, prob_left_node, right_node), -prob_left_node)


def observation_prob(outputs, probs):
    prob = 1
    for name,p in probs.items():
        if outputs[name] == 1:
            p = 1 - p
        prob *= p
    return prob


def naive_sorter(combinations, probs):
    x = [(outputs, observation_prob(outputs, probs)) for outputs in combinations]
    y = sorted(x, key=operator.itemgetter(1), reverse=True)
    a,b = zip(*y)
    return a


def generate_random_outputs(outputs_names):
    return [round(random.uniform(0, 1)) for _ in outputs_names]
    # return {out: round(random.uniform(0, 1)) for out in outputs_names}


def observation_lexicographic_iterator(outputs_names, p):
    """
    iterate all combinations of outputs in by number of flips from original output and by lexicographic order
    this order will ensure few flips will have more probability, will prevent checking the same combinations twice
    :param outputs_names: list of the names of the outputs
    :param p: probability for an output flip
    :return: an observation iterator in lexicographic order, each paired with its normalized probability
    """
    outputs = generate_random_outputs(outputs_names)
    queue = deque([(outputs, -1, 0)])
    length = len(outputs_names)
    normalization_val = calc_normalization_val(length, p)

    while queue:
        outputs, max_in_subset, num_of_flips = queue.popleft()
        yield outputs, pow(p,num_of_flips) / normalization_val
        if max_in_subset == length - 1:
            continue
        for i in range(length - max_in_subset - 1):
            i += max_in_subset + 1
            copy = outputs[:]
            copy[i] = 1 - copy[i]
            queue.append((copy, i, num_of_flips + 1))


def calc_normalization_val(n, p):
    return sum(sc.comb(n,k) * pow(p,k) for k in range(n+1))