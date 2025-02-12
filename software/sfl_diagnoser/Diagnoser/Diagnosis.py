__author__ = 'amir'


class Diagnosis:
    def __init__(self, diagnosis=None, prob=0.0):
        if diagnosis is None:
            diagnosis = []
        self.diagnosis = sorted(diagnosis)
        self.probability = prob

    def clone(self):
        res=Diagnosis()
        res.diagnosis = list(self.diagnosis)
        res.probability = self.get_prob()
        return res

    def get_diag(self):
        return self.diagnosis

    def get_prob(self):
        return self.probability

    def __str__(self):
        return str(sorted(self.diagnosis))+" P: "+str(self.probability)

    def __repr__(self):
        return str(sorted(self.diagnosis))+" P: "+str(self.probability)

    def as_dict(self):
        return {'_diagnosis': map(lambda f: {'_name': f}, sorted(self.diagnosis)), '_probability': self.probability}







