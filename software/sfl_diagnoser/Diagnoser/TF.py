__author__ = 'amir'

# from pyswarm import pso
# from software.sfl_diagnoser.Diagnoser.LightPSO import LightPSO
import operator
import functools

instances = []
calls = 0

def add(tf):
    global instances, calls
    calls += 1
    len_d = len(tf.diagnosis)
    func = []
    h = [1 for _ in tf.diagnosis]
    step = 1.0 / (11 * len_d)
    func.append((h, tf.probabilty_TF(h)))
    for i in range(len_d * 10):
        h = [1 - (i * step) for _ in tf.diagnosis]
        func.append((h, tf.probabilty_TF(h)))
    for instance in filter(lambda inst: len_d == len(inst.diagnosis), instances):
        equals = True
        for h,val in func:
            if instance.probabilty_TF(h) != val:
                equals = False
                break
        if equals:
            tf.max_value = instance.max_value
            return
    tf.maximize()
    instances.append(tf)

class TF(object):
    def __init__(self, matrix, error, diagnosis):
        self.activity = list(zip(map(tuple, matrix), error))
        self.diagnosis = diagnosis
        self.active_components = dict(map(lambda a: (a[0], list(filter(functools.partial(tuple.__getitem__, a[0]), self.diagnosis))), self.activity))
        self.max_value = None
        # add(self)

    def probabilty(self, h_dict):
        def test_prob(v, e):
            # if e==0 : h1*h2*h3..., if e==1: 1-h1*h2*h3...
            return e + ((-2.0 * e + 1.0 ) * functools.reduce(operator.mul,
                                                   list(map(h_dict.get, self.active_components[v])), 1.0))
        return functools.reduce(operator.mul, [test_prob(*act) for act in self.activity], 1.0)
        # return functools.reduce(operator.mul, map(functools.partial(apply, test_prob), self.activity), 1.0)

    def probabilty_TF(self, h):
        return -self.probabilty(dict(zip(self.diagnosis, h)))

    def not_saved(self):
        pass

    def maximize(self):
        if self.max_value == None:
            self.not_saved()
            initialGuess=[0.1 for _ in self.diagnosis]
            lb = [0 for _ in self.diagnosis]
            ub = [1 for _ in self.diagnosis]
            import scipy.optimize
            self.max_value = -scipy.optimize.minimize(self.probabilty_TF,initialGuess,method="L-BFGS-B"
                                        ,bounds=list(zip(lb,ub)), tol=1e-2,options={'maxiter':10}).fun
            # self.max_value = -scipy.optimize.minimize(self.probabilty_TF,initialGuess,method="TNC"
            #                             ,bounds=zip(lb,ub), tol=1e-2,options={'maxiter':10}).fun
            # self.max_value = -scipy.optimize.minimize(self.probabilty_TF,initialGuess,method="SLSQP"
            #                             ,bounds=zip(lb,ub), tol=1e-2,options={'maxiter':10}).fun
            # self.max_value = -scipy.optimize.minimize(self.probabilty_TF,initialGuess,method="trust-constr"
            #                             ,bounds=zip(lb,ub), tol=1e-2,options={'maxiter':10}).fun
            # self.max_value = self.maximize_by_gradient()
            # self.max_value = -pso(self.probabilty_TF, lb, ub, minfunc=1e-3, minstep=1e-3, swarmsize=20,maxiter=10)[1]
            # self.max_value = -self.probabilty_TF(initialGuess)
            # self.max_value = -LightPSO(len(self.diagnosis), self).run()
        return self.max_value

    def calculate(self, values):
        return self.probabilty(values)

    def maximize_by_gradient(self):
        gamma = 0.01
        precision = 1e-3
        prOld = 0
        pr = 1.0
        i = 0
        gj = dict((comp, 0.1) for comp in self.diagnosis)
        while abs(prOld - pr) > precision:
            i += 1
            prOld = pr
            gradients = self.gradient(gj)
            for comp in self.diagnosis:
                val = gj[comp] + gamma * gradients[comp]
                gj[comp] = max(min(val, 1), 0)
            pr = self.calculate(gj)
        return pr

    def gradient(self, vals):
        margin = 0.1
        new_vals = {}
        for comp in vals:
            d1 = self.centralDividedDifference(vals, comp, margin)
            d2 = self.centralDividedDifference(vals, comp, margin/2)
            new_vals[comp] = d2 + ((d2 - d1) / 3)
        return new_vals

    def centralDividedDifference(self, vals, comp, margin):
        val = vals[comp]
        vals[comp] = val + margin
        plus = self.calculate(vals)
        vals[comp] = val - margin
        minus = self.calculate(vals)
        vals[comp] = val
        return (plus-minus)/(2*margin)
