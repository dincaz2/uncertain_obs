import pandas as pd

def file2tuple(file):
    ncomps,ntests,sample = list(map(int, file.split('.')[0].split('_')))
    # ncomps = ncomps + 100 if sample>10 else ncomps
    return ncomps,ntests,sample

a = pd.read_csv(r"C:\Users\deanc\Desktop\workspaces\python\uncertain\software\output\results\accumulating_results\matrices_synthetic.csv")
b = pd.read_csv(r"C:\Users\deanc\Desktop\workspaces\python\uncertain\software\output\results\accumulating_results\without 13.csv")
c = a.append(b)
c.sort_values