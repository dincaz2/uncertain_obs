from software.sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile, write_planning_file, write_merged_matrix
from software.sfl_diagnoser.Diagnoser.Diagnosis_Results import Diagnosis_Results

base = readPlanningFile(r"temp_matrix.txt")
base.diagnose()
res = Diagnosis_Results(base.diagnoses, base.initial_tests, base.error)
print(res.get_metrics_names())
print(res.get_metrics_values())
