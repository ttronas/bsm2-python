import sys
import os
path_name = os.path.dirname(__file__)
print(path_name)
sys.path.append(path_name + '/..')

import numpy as np
import time
import csv

with open(path_name + '/../data/bsm2_values_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow([1,2,4,6,7])