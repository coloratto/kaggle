#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 23:14:18 2015

@author: ngaude
"""

from utils import wdir,ddir,header,normalize_file,add_txt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from os.path import basename

from utils import itocat1,itocat2,itocat3
from utils import cat1toi,cat2toi,cat3toi
from utils import cat3tocat2,cat3tocat1,cat2tocat1
from utils import cat1count,cat2count,cat3count
from utils import training_sample
from os.path import isfile

from joblib import Parallel, delayed
import time

def vectorizer(txt):
    vec = TfidfVectorizer(
        min_df = 2,
        stop_words = None,
        max_features=123456,
        smooth_idf=True,
        norm='l2',
        sublinear_tf=True,
        use_idf=True,
        ngram_range=(1,2))
    X = vec.fit_transform(txt)
    return (vec,X)

def create_sample(df,label,mincount,maxsampling):
    fname = ddir+'training_sampled_'+label+'.csv'
    dfsample = training_sample(df,label,mincount,maxsampling)
    dfsample.to_csv(fname,sep=';',index=False,header=False)
    return dfsample

def training_stage1(dftrain,dfvalid):
    fname = ddir + 'joblib/stage1'
    print '-'*50
    print 'training',basename(fname)
    df = dftrain
    dfv = dfvalid
    vec,X = vectorizer(df.txt)
    Y = df['Categorie1'].values
    cla = LogisticRegression(C=5)
    cla.fit(X,Y)
    labels = np.unique(df.Categorie1)
    Xv = vec.transform(dfv.txt)
    Yv = dfv['Categorie1'].values
    sct = cla.score(X[:10000],Y[:10000])
    scv = cla.score(Xv,Yv)
    joblib.dump((labels,vec,cla),fname)
    del X,Y,Xv,Yv,vec,cla
    return sct,scv

def training_stage2(dftrain,dfvalid,cat1,i):
    fname = ddir + 'joblib/stage2_'+str(cat1)
    df = dftrain[dftrain.Categorie1 == cat1].reset_index(drop=True)
    dfv = dfvalid[dfvalid.Categorie1 == cat1].reset_index(drop=True)
    labels = np.unique(df.Categorie2)
    if len(labels)<=1:
        joblib.dump((labels,None,None),fname)
        scv = -1
        sct = -1
        print 'stage2 training',cat1,'\t\t(',i,') : N=',len(df),'K=',len(labels)
        print 'stage2 training',cat1,'\t\t(',i,') : training=',sct,'validation=',scv
        return (sct,scv)
    vec,X = vectorizer(df.txt)
    Y = df['Categorie2'].values
    cla = LogisticRegression(C=5)
    cla.fit(X,Y)
    labels = np.unique(df.Categorie2)
    sct = cla.score(X[:min(10000,len(df))],Y[:min(10000,len(df))])
    if len(dfv)==0:
        scv = -1
    else:
        Xv = vec.transform(dfv.txt)
        Yv = dfv['Categorie2'].values
        scv = cla.score(Xv,Yv)
    print 'stage 2 training',cat1,'\t\t(',i,') : N=',len(df),'K=',len(labels)
    print 'stage 2 training',cat1,'\t\t(',i,') : training=',sct,'validation=',scv
    joblib.dump((labels,vec,cla),fname)
    del vec,cla
    return (sct,scv)

def training_stage3(dftrain,dfvalid,cat2,i):
    fname = ddir + 'joblib/stage3_'+str(cat2)
    df = dftrain[dftrain.Categorie2 == cat2].reset_index(drop=True)
    dfv = dfvalid[dfvalid.Categorie2 == cat2].reset_index(drop=True)
    labels = np.unique(df.Categorie3)
    if len(labels)<=1:
        joblib.dump((labels,None,None),fname)
        scv = -1
        sct = -1
        print 'stage 3 training',cat2,'\t\t(',i,') : N=',len(df),'K=',len(labels)
        print 'stage 3 training',cat2,'\t\t(',i,') : training=',sct,'validation=',scv
        return (sct,scv)
    vec,X = vectorizer(df.txt)
    Y = df['Categorie3'].values
    cla = LogisticRegression(C=5)
    cla.fit(X,Y)
    labels = np.unique(df.Categorie3)
    sct = cla.score(X[:min(10000,len(df))],Y[:min(10000,len(df))])
    if len(dfv)==0:
        scv = -1
    else:
        Xv = vec.transform(dfv.txt)
        Yv = dfv['Categorie3'].values
        scv = cla.score(Xv,Yv)
    print 'stage 3 training',cat2,'\t\t(',i,') : N=',len(df),'K=',len(labels)
    print 'stage 3 training',cat2,'\t\t(',i,') : training=',sct,'validation=',scv
    joblib.dump((labels,vec,cla),fname)
    del vec,cla
    return (sct,scv)


#####################
# create sample set 
# from training set
#####################

# NOTE : USE analyse_test.py and perfect_sampling.py to get perfect training & validation set
# NOTE : USE analyse_test.py and perfect_sampling.py to get perfect training & validation set
# NOTE : USE analyse_test.py and perfect_sampling.py to get perfect training & validation set
# NOTE : USE analyse_test.py and perfect_sampling.py to get perfect training & validation set

#######################
# training
# stage1 : Categorie1 
# stage3 : Categorie3|Categorie1
#######################

dftrain = pd.read_csv(ddir+'training_perfect_200.csv',sep=';',names = header()).fillna('')
dfvalid = pd.read_csv(ddir+'validation_perfect.csv',sep=';',names = header()).fillna('')
dftest = pd.read_csv(ddir+'test_normed.csv',sep=';',names = header(test=True)).fillna('')

add_txt(dftrain)
add_txt(dfvalid)
add_txt(dftest)

dftrain = dftrain[['Categorie3','Categorie2','Categorie1','txt']]
dfvalid = dfvalid[['Categorie3','Categorie2','Categorie1','txt']]
dftest = dftest[['Identifiant_Produit','txt']]

# training stage1

dt = -time.time()
sct,scv = training_stage1(dftrain,dfvalid)
dt += time.time()

print '##################################'
print '# stage1 elapsed time :',dt
print '# stage1 training score :',sct
print '# stage1 validation score :',scv
print '##################################'

# training Parallel stage2
dfts = []
dfvs = []

for cat1 in itocat1:
    dfts.append(dftrain[dftrain.Categorie1 == cat1].reset_index(drop=True))
    dfvs.append(dfvalid[dfvalid.Categorie1 == cat1].reset_index(drop=True))

dt = -time.time()
scs = Parallel(n_jobs=3)(delayed(training_stage2)(dft,dfv,cat1,i) for i,(dft,dfv,cat1) in enumerate(zip(dfts,dfvs,itocat1)))
dt += time.time()

sct = np.median([s for s in zip(*scs)[0] if s>=0])
scv = np.median([s for s in zip(*scs)[1] if s>=0])

print '##################################'
print '# stage2 elapsed time :',dt
print '# stage2 training score :',sct
print '# stage2 validation score :',scv
print '##################################'

# training Parallel stage3
dfts = []
dfvs = []

for cat2 in itocat2:
    dfts.append(dftrain[dftrain.Categorie2 == cat2].reset_index(drop=True))
    dfvs.append(dfvalid[dfvalid.Categorie2 == cat2].reset_index(drop=True))

dt = -time.time()
scs = Parallel(n_jobs=3)(delayed(training_stage3)(dft,dfv,cat2,i) for i,(dft,dfv,cat2) in enumerate(zip(dfts,dfvs,itocat2)))
dt += time.time()

sct = np.median([s for s in zip(*scs)[0] if s>=0])
scv = np.median([s for s in zip(*scs)[1] if s>=0])

print '##################################'
print '# stage3 elapsed time :',dt
print '# stage3 training score :',sct
print '# stage3 validation score :',scv
print '##################################'

#######################
# predicting
#######################

# predict : 
# P(Categorie2) = P(Categorie1) *  P(Categorie2|Categorie1)
# P(Categorie3) = P(Categorie2) *  P(Categorie3|Categorie2)

def log_proba(df,vec,cla):
    assert 'txt' in df.columns
    X = vec.transform(df.txt)
    lp = cla.predict_log_proba(X)
    return (cla.classes_,lp)

dfvalid = pd.read_csv(ddir+'validation_perfect.csv',sep=';',names = header()).fillna('').reset_index()
dftest = pd.read_csv(ddir+'test_normed.csv',sep=';',names = header(test=True)).fillna('')

add_txt(dfvalid)
add_txt(dftest)

#######################
# stage 1 log proba filling
#######################
stage1_log_proba_valid = np.full(shape=(len(dfvalid),cat1count),fill_value = -666.,dtype = float)
stage1_log_proba_test = np.full(shape=(len(dftest),cat1count),fill_value = -666.,dtype = float)

fname = ddir + 'joblib/stage1'
(labels,vec,cla) = joblib.load(fname)
(classes,lpv) = log_proba(dfvalid,vec,cla)
(classes,lpt) = log_proba(dftest,vec,cla)
for i,k in enumerate(classes):
    j = cat1toi[k]
    stage1_log_proba_valid[:,j] = lpv[:,i]
    stage1_log_proba_test[:,j] = lpt[:,i]

del labels,vec,cla

#######################
# stage 2 log proba filling
#######################
stage2_log_proba_valid = np.full(shape=(len(dfvalid),cat2count),fill_value = -666.,dtype = float)
stage2_log_proba_test = np.full(shape=(len(dftest),cat2count),fill_value = -666.,dtype = float)

for ii,cat1 in enumerate(itocat1):
    fname = ddir + 'joblib/stage2_'+str(cat1)
    print '-'*50
    print 'predicting',basename(fname),':',ii,'/',len(itocat1)
    if not isfile(fname): 
        continue
    (labels,vec,cla) = joblib.load(fname)
    if len(labels)==0:
        print 'prediction for',cat1,' is impossible'
        continue
    if len(labels)==1:
        k = labels[0]
        j = cat2toi[k]
        stage2_log_proba_valid[:,j] = 0
        stage2_log_proba_test[:,j] = 0
        continue
    (classes,lpv) = log_proba(dfvalid,vec,cla)
    (classes,lpt) = log_proba(dftest,vec,cla)
    for i,k in enumerate(classes):
        j = cat2toi[k]
        stage2_log_proba_valid[:,j] = lpv[:,i]
        stage2_log_proba_test[:,j] = lpt[:,i]
    del labels,vec,cla



#######################
# stage 3 log proba filling
#######################
stage3_log_proba_valid = np.full(shape=(len(dfvalid),cat3count),fill_value = -666.,dtype = float)
stage3_log_proba_test = np.full(shape=(len(dftest),cat3count),fill_value = -666.,dtype = float)

for ii,cat2 in enumerate(itocat2):
    fname = ddir + 'joblib/stage3_'+str(cat2)
    print '-'*50
    print 'predicting',basename(fname),':',ii,'/',len(itocat2)
    if not isfile(fname): 
        continue
    (labels,vec,cla) = joblib.load(fname)
    if len(labels)==0:
        print 'prediction for',cat2,' is impossible'
        continue
    if len(labels)==1:
        k = labels[0]
        j = cat3toi[k]
        stage3_log_proba_valid[:,j] = 0
        stage3_log_proba_test[:,j] = 0
        continue
    (classes,lpv) = log_proba(dfvalid,vec,cla)
    (classes,lpt) = log_proba(dftest,vec,cla)
    for i,k in enumerate(classes):
        j = cat3toi[k]
        stage3_log_proba_valid[:,j] = lpv[:,i]
        stage3_log_proba_test[:,j] = lpt[:,i]
    del labels,vec,cla

print '>>> dump stage1 & stage2 & stage3 log_proba'
joblib.dump((stage1_log_proba_valid,stage2_log_proba_valid,stage3_log_proba_valid),ddir+'/joblib/log_proba_valid')
joblib.dump((stage1_log_proba_test,stage2_log_proba_test,stage3_log_proba_test),ddir+'/joblib/log_proba_test')
print '<<< dump stage1 & stage2 & stage3 log_proba'


##################
# (stage1_log_proba_valid,stage2_log_proba_valid,stage3_log_proba_valid) = joblib.load(ddir+'/joblib/log_proba_valid')
# (stage1_log_proba_test,stage2_log_proba_test,stage3_log_proba_test) = joblib.load(ddir+'/joblib/log_proba_test')
##################

##################
# bayes rulez ....
##################

assert stage1_log_proba_valid.shape[1] == stage1_log_proba_test.shape[1]
assert stage2_log_proba_valid.shape[1] == stage2_log_proba_test.shape[1]
assert stage3_log_proba_valid.shape[1] == stage3_log_proba_test.shape[1]

for i in range(stage2_log_proba_valid.shape[1]):
    cat2 = itocat2[i]
    cat1 = cat2tocat1[cat2]
    j = cat1toi[cat1]
    stage2_log_proba_valid[:,i] += stage1_log_proba_valid[:,j]
    stage2_log_proba_test[:,i] += stage1_log_proba_test[:,j]

for i in range(stage3_log_proba_valid.shape[1]):
    cat3 = itocat3[i]
    cat2 = cat3tocat2[cat3]
    j = cat2toi[cat2]
    stage3_log_proba_valid[:,i] += stage2_log_proba_valid[:,j]
    stage3_log_proba_test[:,i] += stage2_log_proba_test[:,j]


predict_cat1_valid = [itocat1[i] for i in np.argmax(stage1_log_proba_valid,axis=1)]
predict_cat2_valid = [itocat2[i] for i in np.argmax(stage2_log_proba_valid,axis=1)]
predict_cat3_valid = [itocat3[i] for i in np.argmax(stage3_log_proba_valid,axis=1)]

predict_cat1_test = [itocat1[i] for i in np.argmax(stage1_log_proba_test,axis=1)]
predict_cat2_test = [itocat2[i] for i in np.argmax(stage2_log_proba_test,axis=1)]
predict_cat3_test = [itocat3[i] for i in np.argmax(stage3_log_proba_test,axis=1)]

def submit(df,Y):
    submit_file = ddir+'resultat.csv'
    df['Id_Produit']=df['Identifiant_Produit']
    df['Id_Categorie'] = Y
    df= df[['Id_Produit','Id_Categorie']]
    df.to_csv(submit_file,sep=';',index=False)

score_cat1 = sum(dfvalid.Categorie1 == predict_cat1_valid)*1.0/len(dfvalid)
score_cat2 = sum(dfvalid.Categorie2 == predict_cat2_valid)*1.0/len(dfvalid)
score_cat3 = sum(dfvalid.Categorie3 == predict_cat3_valid)*1.0/len(dfvalid)
print 'validation score :',score_cat1,score_cat2,score_cat3
submit(dftest,predict_cat3_test)

##########################
# reference model score  #
##########################
#
################################################
# NOTE : training_perfect_200.csv file
################################################
# stage1 elapsed time : 1182.08965111
# stage1 training score : 0.9633
# stage1 validation score : 0.860583523033
# stage3 elapsed time : 1157.06438398
# stage3 training score : 0.987830964724
# stage3 validation score : 0.825870646766
# validation score : 0.861331851888 0.630661095143 (validation_normed)
# validation score : 0.86082680244 0.665195405495 (validation_perfect)
# (resultat43.csv) test score : 64,50633% (REF)
##################################

##########################
# THIS MODEL             #
##########################

#################################################
# NOTE : training_perfect_200.csv file
# NOTE : stage1 => stage2 => stage3
#################################################
# stage1 elapsed time : 966.20471406
# stage1 training score : 0.9633
# stage1 validation score : 0.874375015096
# stage2 elapsed time : 129.804960012
# stage2 training score : 0.995263870095
# stage2 validation score : 0.9164589257
# stage3 elapsed time : 112.83743
# stage3 training score : 0.996232733361
# stage3 validation score : 0.898305084746
# validation score : 0.86082680244 0.753332059013 0.664795732184
# (resultat56.csv) test score 64,55217% (TRY)
##################################


#################################################
# stage1 elapsed time : 966.20471406
# stage1 training score : 0.9633
# stage1 validation score : 0.874375015096
# stage3 elapsed time : ~1500
# stage3 training score : 0.984027777778
# stage3 validation score : 0.863612147043
# validation score : 0.874375015096 0.68585299872
# (result30.csv) test score : 63,99060%
#################################################
#
#################################################
# stage1 elapsed time : 448.81675601
# stage1 training score : 0.9569
# stage1 validation score : 0.874882249221
# stage3 elapsed time : 765.464223146
# stage3 training score : 0.9839
# stage3 validation score : 0.857221006565
# validation score : 0.874882249221 0.684452066375
# (result31.csv) test score : 64,01352%
#################################################
#
#################################################
# TEST WITH NEW validation_perfect.csv file ....
# stage1 elapsed time : 1182.08965111
# stage1 training score : 0.9633
# stage1 validation score : 0.860583523033
# stage3 elapsed time : 1195.13887191
# stage3 training score : 0.984027777778
# stage3 validation score : 0.835164835165
# validation score : 0.860583523033 0.69124367908
#################################################



