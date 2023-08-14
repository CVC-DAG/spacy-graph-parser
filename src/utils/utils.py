from Levenshtein import distance
from scipy.optimize import linear_sum_assignment
import numpy as np

def edit_distance(w1, w2):
    return distance(w1, w2)

def hungarian_distance(s1, s2, word_distance = edit_distance):
    s1_split, s2_split = s1.split(), s2.split()
    weights_matrix = np.zeros((len(s1_split), len(s2_split)))
    
    for n, word_s1 in enumerate(s1_split):
        for m, word_s2 in enumerate(s2_split):
            weights_matrix[n, m] = word_distance(word_s1, word_s2)

    row_ind, col_ind = linear_sum_assignment(weights_matrix)
    return weights_matrix[row_ind, col_ind].sum()