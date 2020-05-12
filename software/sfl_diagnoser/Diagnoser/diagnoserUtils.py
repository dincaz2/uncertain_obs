import software.sfl_diagnoser.Diagnoser.ExperimentInstance
from software.sfl_diagnoser.Diagnoser.FullMatrix import FullMatrix
from software.sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from functools import reduce, partial

__author__ = 'amir'

import csv

def readMatrixWithProbabilitiesFile(fileName):
    reader=csv.reader(open(fileName,"r"))
    lines=[x for x in reader]
    probabilies=[float(x) for x in  lines[0][:-1]]
    matrix=[]
    error=[]
    lines=[[int(y) for y in x ] for x in lines[1:]]
    for line in lines:
        error.append(line[-1])
        matrix.append(line[:-1])
    ans= FullMatrix()
    ans.probabilities=probabilies
    ans.matrix=matrix
    ans.error=error
    return ans

def cut_matrix(test_pool, error, all_comps, initials):
    # keeping only components touching failing tests, and tests touched by these components
    test_pool = test_pool.copy()
    failing_tests = set(test for test, out in error.items() if out == 1)
    all_touching_comps = set()
    for test in  failing_tests:
        all_touching_comps |= set(test_pool[test])
    for test,comps in list(test_pool.items()):
        new_comps = sorted(set(comps) & all_touching_comps)
        if new_comps:
            test_pool[test] = new_comps
        else:
            del test_pool[test]
    remaining_tests = list(test_pool.keys())
    error = {test:out for test,out in error.items() if test in remaining_tests}
    remaining_comps = {key:name for key,name in all_comps.items() if key in all_touching_comps}
    initials = [t for t in initials if t in remaining_tests]
    return test_pool, error, remaining_comps, initials


def readPlanningFile(fileName, delimiter=";", cut=False):
    lines=open(fileName,"r").readlines()
    lines=[x.replace("\n","") for x in lines]
    sections=["[Description]", "[Components names]", "[Priors]","[Bugs]","[InitialTests]","[TestDetails]"]
    sections=[lines.index(x) for x in sections]
    description, components_names, priorsStr,BugsStr,InitialsStr,TestDetailsStr=tuple([lines[x[0]+1:x[1]] for x in zip(sections,sections[1:]+[len(lines)])])
    priors=eval(priorsStr[0])
    bugs=eval(BugsStr[0])
    initials=eval(InitialsStr[0])
    try:
        components = dict(map(lambda x: x if isinstance(x, tuple) else eval(x), eval(components_names[0].replace(delimiter, ',') + ',')))
    except:
        components = dict(eval(eval(components_names[0].replace(delimiter, ','))))
    testsPool={}
    estimatedTestsPool = {}
    error={}
    for td in TestDetailsStr:
        tup = tuple(td.split(delimiter))
        ind, actualTrace, err = None, None, None
        if len(tup) == 3:
            ind, actualTrace, err = tup
        if len(tup) == 4:
            ind, actualTrace, estimatedTrace, err = tup
            estimatedTestsPool[ind] = eval(estimatedTrace)
        actualTrace=eval(actualTrace)
        err=int(err)
        testsPool[ind] = actualTrace
        error[ind] = err

    # testsPool['T1'] = [0,3] #TODO: delete
    # testsPool['T3'] = [2,3]
    old = None
    if cut:
        old = components, initials
        testsPool, error, components, initials = cut_matrix(testsPool, error, components, initials)
    Experiment_Data().set_values(priors, bugs, testsPool, components, estimatedTestsPool)
    return partial(software.sfl_diagnoser.Diagnoser.ExperimentInstance.ExperimentInstance, initials), error, initials, old
    # return software.sfl_diagnoser.Diagnoser.ExperimentInstance.ExperimentInstance(initials, error)


def diagnoseTests():
    full = readMatrixWithProbabilitiesFile("C:\GitHub\matrix\OPT__Rand.csv")
    print("full",[x.diagnosis for x in full.diagnose()])
    ds = full.convetTodynamicSpectrum()
    matrix_ = ds.convertToFullMatrix()
    print("matrix",[x.diagnosis for x in matrix_.diagnose()])
    Fullm,chosen= FullMatrix.optimize_FullMatrix(matrix_)
    print("matrixOPT",[x.diagnosis for x in Fullm.diagnose()]) ## should result wrong comps!!
    print([x.diagnosis for x in ds.diagnose()])




def readMatrixTest():
    global full, ds
    full = readMatrixWithProbabilitiesFile("C:\GitHub\matrix\OPT__Rand.csv")
    print(full.probabilities, len(full.probabilities))
    print(full.error[0])
    print(full.matrix[0])
    ds = full.convetTodynamicSpectrum()
    print(ds.probabilities)
    print(ds.error[0])
    print(ds.TestsComponents[0])
    matrix_ = ds.convertToFullMatrix()
    print(matrix_.probabilities)
    opt = FullMatrix.optimize_FullMatrix(matrix_)
    print(opt.probabilities)
    print(len(opt.error), len(matrix_.error))



def readPlannerTest():
    global instance
    print("planner")
    file="C:\projs\\40_uniform_9.txt"
    instance = readPlanningFile(file)
    # print(instance.priors)
    # print(instance.error)
    # print(instance.bugs)
    # print(instance.initial_tests)
    # print(instance.pool[0])
    instance.initial_tests=range(len(instance.error))
    instance.diagnose()
    print([x.diagnosis for x in instance.diagnoses])
    ds=instance.initials_to_DS()
    print([x.diagnosis for x in ds.diagnose()])
    fm=ds.convertToFullMatrix()
    print([x.diagnosis for x in fm.diagnose()])

    # print(fm.error)
    # for i in range(len(fm.error)):
    #     print(fm.matrix[i])

def write_planning_file(out_path,
                        bugs,
                        tests_details,
                        description="default description",
                        priors=None,
                        initial_tests=None,
                        delimiter=";"):
    """
    write a matrix to out path
    :param out_path: destination path to write the matrix
    :param bugs: list of bugged components
    :param tests_details: list of tuples of (name, trace, outcome).
     trace is set of components. outcome is 0 if test pass, 1 otherwise
    :param description: free text that describe the matrix. optional
    :param priors: map between components and priors probabilities of each component. optional
    :param initial_tests: list of tests for the initial matrix. optional
    :return:
    """
    # get the components names from the traces
    components_names = list(set(reduce(list.__add__, map(lambda details: details[1], tests_details), [])))
    map_component_id = dict(map(lambda x: tuple(reversed(x)), list(enumerate(components_names))))
    full_tests_details = []
    if len(tests_details[0]) == 3:
        for name, trace, outcome in tests_details:
            full_tests_details.append((name, sorted(map(lambda comp: map_component_id[comp] , trace), key=lambda x:x), outcome))
    else:
        for name, trace, estimated_trace, outcome in tests_details:
            full_tests_details.append((name, sorted(map(lambda comp: map_component_id[comp] , trace), key=lambda x:x), estimated_trace, outcome))
    if priors is None:
        priors = dict(((component, 0.1) for component in components_names))
    if initial_tests is None:
        initial_tests = list(map(lambda details: details[0], tests_details))
    bugged_components = [map_component_id[component] for component in filter(lambda c: any(map(lambda b: b in c, bugs)),components_names)]
    lines = [["[Description]"]] + [[description]]
    lines += [["[Components names]"]] + [list(enumerate(components_names))]
    lines += [["[Priors]"]] + [[[priors[component] for component in components_names]]]
    lines += [["[Bugs]"]] + [[bugged_components]]
    lines += [["[InitialTests]"]] + [[initial_tests]]
    lines += [["[TestDetails]"]] + full_tests_details
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(lines)

def write_merged_matrix(instance, out_matrix):
    componets = instance.get_components_vectors()
    similiar_componets = {}
    for component in componets:
        similiar_componets.setdefault(str(sorted(componets[component])), []).append(component)
    new_components_map = {}
    for comp in similiar_componets:
        candidates = similiar_componets[comp]
        new_name = "^".join(similiar_componets[comp])
        for candidate in candidates:
            new_components_map[candidate] = new_name
    get_name = lambda index: new_components_map.get(Experiment_Data().COMPONENTS_NAMES[index], Experiment_Data().COMPONENTS_NAMES[index])
    new_bugs = map(get_name, Experiment_Data().BUGS)
    new_pool = map(lambda test: [test, list(set(map(get_name, Experiment_Data().POOL[test]))), instance.error[test]], Experiment_Data().POOL)
    write_planning_file(out_matrix, new_bugs, new_pool)

def save_ds_to_matrix_file(ds, out_file):
    tests_details = map(lambda details: (
    str(details[0]), map(lambda c: Experiment_Data().COMPONENTS_NAMES[c], details[1]), details[2]),
                        list(zip(ds.tests_names, ds.TestsComponents, ds.error)))
    write_planning_file(out_file, map(lambda c: Experiment_Data().COMPONENTS_NAMES[c], Experiment_Data().BUGS), tests_details)
