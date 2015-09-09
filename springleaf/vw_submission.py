import pandas as pd
import numpy as np

df = pd.read_csv('data/sample_submission.csv')

with open('data/vw_test.pred','r') as f:
    target = [float(line.split()[0]) for line in f]

target  =  1./(1+np.exp(-np.array(target)))

df['target'] = target 

print 'average target',np.mean(target)

df.to_csv('data/vw_submission.csv',index=False)
