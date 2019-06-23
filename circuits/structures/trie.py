def make_trie():
    return {True:False}

def add_to_trie(trie, diagnose):
    if not diagnose:
        trie[True] = True # special representation for the empty diagnose
    curr = trie
    for comp in diagnose:
        curr = curr.setdefault(comp.name, {})

def check_trie_for_subsets(trie, diagnose, i=0, root=True):
    if root and trie[True]: # if empty diagnose is a diagnose (represented as True in the root) then every diagnose is a superset of it
        return True
    if not root and not trie: # if reached the end of a branch (a diagnose) then we found a subset
        return True
    if i == len(diagnose): # if finished scanning the diagnose and didn't reach a leaf in the trie then no subset found
        return False

    # trie not empty - traverse comps
    comp = diagnose[i]
    if comp.name in trie and check_trie_for_subsets(trie[comp.name], diagnose, i+1, False):
        return True
    return check_trie_for_subsets(trie, diagnose, i+1, False)
