import copy
from software.sfl_diagnoser.Diagnoser import Diagnosis
import software.sfl_diagnoser.Diagnoser.dynamicSpectrum
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
import software.sfl_diagnoser.Diagnoser.diagnoserUtils
import math
from software.sfl_diagnoser.Diagnoser import Diagnosis
from software.sfl_diagnoser.Diagnoser import Staccato
from software.sfl_diagnoser.Diagnoser import TF
from collections import deque
import numpy as np

class FastBarinel:
    def __init__(self, initial_tests, error):
        self.TestsComponents = copy.deepcopy([Experiment_Data().POOL[test] for test in initial_tests])
        self.prior_probs = list(Experiment_Data().PRIORS)
        self.M_matrix = list(
            map(lambda test: list(map(lambda comp: 1 if comp in test else 0, range(len(self.prior_probs)))),
                self.TestsComponents))
        self.initial_e_vector = [error[test] for test in initial_tests]
        # self.tests_names = list(initial_tests)

    def binom(self, n, p, k):
        x = k * np.log2(p) + (n - k) * np.log2(1 - p)
        return pow(2, x)

    def error_generator(self, length, p):
        """
        iterate all combinations of error vectors by number of ones (failed tests) and by lexicographic order
        :param length: length of each vector (number of components)
        :param p: probability for a faulty output sensor
        :return: an observation iterator in lexicographic order, each paired with its probability
        """

        error_vec =  [0] * length
        queue = deque([(error_vec, None, -1)])

        saved_probs = {}

        while queue:
            error_vec, parent, max_in_subset = queue.popleft()
            num_of_flips = [a^b for a,b in zip(error_vec, self.initial_e_vector)].count(1)
            obs_prob = saved_probs[num_of_flips] if num_of_flips in saved_probs else saved_probs.setdefault(num_of_flips, self.binom(length, p, num_of_flips))

            yield error_vec, max_in_subset, obs_prob
            if max_in_subset == length - 1:
                continue
            for i in range(max_in_subset + 1, length):
                copy = error_vec[:]
                copy[i] = 1 - copy[i]
                queue.append((copy, error_vec, i))

    def non_uniform_prior(self, diag):
        comps = diag.get_diag()
        prob = 1
        for comp in comps:
            prob *= self.prior_probs[comp]
        return prob

    def generate_probs(self, diagnoses, e_vector, prior_p, normalize=True):
        new_diagnoses = []
        probs_sum = 0.0
        for diag in diagnoses:
            if (self.prior_probs == []):
                dk = math.pow(prior_p,len(diag.get_diag())) #assuming same prior prob. for every component.
            else:
                dk = self.non_uniform_prior(diag)
            tf = TF.TF(self.M_matrix, e_vector, diag.get_diag())
            e_dk = tf.maximize()
            diag.probability=e_dk * dk #temporary probability
            probs_sum += diag.probability
        if normalize:
            for diag in diagnoses:
                temp_prob = diag.get_prob() / probs_sum
                diag.probability=temp_prob
                new_diagnoses.append(diag)
            diagnoses = new_diagnoses
        return diagnoses

    def incremental_mhs(self, old_mhs, new_test_comps):
        comps = set(np.where(np.array(new_test_comps) == 1)[0])
        diags = set()
        for diag in old_mhs:
            if comps & diag:
                diags.add(diag)
            else:
                for comp in comps:
                    new_diag = diag.copy()
                    new_diag.add(comp)
                    diags.add(new_diag)
        return diags

    def diagnose(self, faulty_comp_probs, faulty_output_prob, normalize=True):
        mhs_dict = dict()
        for e_vector, parent_e_vector, failed_test_index, error_prob in self.error_generator(len(self.prior_probs), faulty_output_prob):
            if not parent_e_vector: # first observation is "all tests passed" with only 1 diagnosis - the empty one
                # e_vector = (0,) * len(self.prior_probs)
                mhs_dict[e_vector] = [set()]
                yield Diagnosis.Diagnosis(set(), error_prob)
            else:
                # e_vector = list(parent_e_vector)
                # e_vector[failed_test_index] = 1
                # e_vector = tuple(e_vector)
                diags = self.incremental_mhs(mhs_dict[parent_e_vector], self.M_matrix[failed_test_index])
                mhs_dict[e_vector] = diags
                diagnoses = [Diagnosis.Diagnosis(diag) for diag in diags]

                yield self.generate_probs(diagnoses, e_vector, faulty_comp_probs, normalize), error_prob
                # for diag in self.generate_probs(diagnoses, e_vector, faulty_comp_probs, normalize):
                #     diag.probability *= error_prob
                #     yield diag

    # def diagnose(self, prior_p=0.05, normalize=True):
    #     fullM, chosen = FullMatrix.optimize_FullMatrix(self.convertToFullMatrix())
    #     chosenDict = dict(enumerate(chosen))
    #     Opt_diagnoses = self.run(prior_p, normalize)
    #     diagnoses = []
    #     for diag in Opt_diagnoses:
    #         diag = diag.clone()
    #         diag_comps = [chosenDict[x] for x in diag.diagnosis]
    #         diag.diagnosis = list(diag_comps)
    #         diagnoses.append(diag)
    #     return diagnoses