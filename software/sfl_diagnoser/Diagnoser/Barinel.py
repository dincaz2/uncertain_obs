__author__ = 'amir'

import csv
import math
import sys

from software.sfl_diagnoser.Diagnoser import Diagnosis
from software.sfl_diagnoser.Diagnoser import Staccato
from software.sfl_diagnoser.Diagnoser import TF

prior_p = 0.05

class Barinel:

    def __init__(self):
        self.M_matrix = []
        self.e_vector = []
        self.prior_probs = []
        self.diagnoses = []


    def set_matrix_error(self, M, e):
        self.M_matrix = M
        self.e_vector = e

    def set_prior_probs(self, probs):
        self.prior_probs=probs


    def non_uniform_prior(self, diag):
        comps = diag.get_diag()
        prob = 1
        for i in range(len(comps)):
            prob *= self.prior_probs[comps[i]]
        return prob

    def generate_probs(self, normalize=True):
        new_diagnoses = []
        probs_sum = 0.0
        for diag in self.diagnoses:
            dk = 0.0
            if (self.prior_probs == []):
                dk = math.pow(prior_p,len(diag.get_diag())) #assuming same prior prob. for every component.
            else:
                dk = self.non_uniform_prior(diag)
            tf = TF.TF(self.M_matrix, self.e_vector, diag.get_diag())
            e_dk = tf.maximize()
            diag.probability=e_dk * dk #temporary probability
            probs_sum += diag.probability
        if normalize:
            for diag in self.diagnoses:
                temp_prob = diag.get_prob() / probs_sum
                diag.probability=temp_prob
                new_diagnoses.append(diag)
            self.diagnoses = new_diagnoses


    def run(self, normalize=True):
        #initialize
        self.diagnoses = []
        diags = Staccato.Staccato().run(self.M_matrix, self.e_vector)
        for diag in diags:
            self.diagnoses.append(Diagnosis.Diagnosis(diag))
        #generate probabilities
        self.generate_probs(normalize)

        return self.diagnoses
