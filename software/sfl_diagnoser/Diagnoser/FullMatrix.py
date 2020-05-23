from software.sfl_diagnoser.Diagnoser import Barinel
from functools import reduce


class FullMatrix(object):
    def __init__(self):
        self.matrix=[] # matrix size define the num of tests
        self.probabilities=[] # probabilities size define the num of components
        self.error=[]

    def diagnose(self, normalize=True):
        bar= Barinel.Barinel()
        bar.set_matrix_error(self.matrix,self.error)
        bar.set_prior_probs(self.probabilities)
        return bar.run(normalize)

    def save_to_csv_file(self, out_file):
        import csv
        lines = [self.probabilities] + list(map(lambda x : x[0] + [x[1]] ,list(zip(self.matrix, self.error))))
        with open(out_file, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(lines)

    # optimization: remove unreachable components & components that pass all their tests
    # return: optimized FullMatrix, chosen_components( indices)
    @staticmethod
    def optimize_FullMatrix(fullMatrix):
        failed_tests = list(map(lambda test: list(enumerate(test[0])), filter(lambda test: test[1] == 1, zip(fullMatrix.matrix, fullMatrix.error))))
        used_components = reduce(set.__or__, map(lambda test: set(map(lambda comp: comp[0], filter(lambda comp: comp[1] == 1, test))), failed_tests), set())
        optimizedMatrix = FullMatrix()
        optimizedMatrix.probabilities = [x[1] for x in enumerate(fullMatrix.probabilities) if x[0] in used_components]
        newErr = []
        newMatrix = []

        for test, err in zip(fullMatrix.matrix, fullMatrix.error):
            newTest = [x[1] for x in enumerate(test) if x[0] in used_components]
            if 1 in newTest: ## optimization could remove all comps of a test
                newMatrix.append(newTest)
                newErr.append(err)
        optimizedMatrix.matrix = newMatrix
        optimizedMatrix.error = newErr
        return optimizedMatrix, sorted(used_components)
