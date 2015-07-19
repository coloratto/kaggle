import marisa_trie
from sklearn.externals import six
from sklearn.feature_extraction.text import TfidfVectorizer
import Stemmer
import nltk
from bs4 import BeautifulSoup
import re
import unicodedata 
import time
import pandas as pd
import numpy as np
#ddir = 'E:/workspace/data/cdiscount/'
#wdir = 'C:/Users/ngaude/Documents/GitHub/kaggle/cdiscount/'
ddir = '/home/ngaude/workspace/data/cdiscount/'
wdir = '/home/ngaude/workspace/github/kaggle/cdiscount/'


rayon = pd.read_csv(ddir+'rayon.csv',sep=';')

itocat1 = list(np.unique(rayon.Categorie1))
cat1toi = {cat1:i for i,cat1 in enumerate(itocat1)}
itocat2 = list(np.unique(rayon.Categorie2))
cat2toi = {cat2:i for i,cat2 in enumerate(itocat2)}
itocat3 = list(np.unique(rayon.Categorie3))
cat3toi = {cat3:i for i,cat3 in enumerate(itocat3)}
cat3tocat2 = rayon.set_index('Categorie3').Categorie2.to_dict()
cat3tocat1 = rayon.set_index('Categorie3').Categorie1.to_dict()
cat1count = len(np.unique(rayon.Categorie1))
cat2count = len(np.unique(rayon.Categorie2))
cat3count = len(np.unique(rayon.Categorie3))


stopwords = []
with open(wdir+'stop-words_french_1_fr.txt', "r") as f:
    stopwords += f.read().split('\n')

with open(wdir+'stop-words_french_2_fr.txt', "r") as f:
    stopwords += f.read().split('\n')

stopwords += nltk.corpus.stopwords.words('french')
stopwords += ['voir', 'presentation']
stopwords = set(stopwords)
stemmer = Stemmer.Stemmer('french')

def header(test=False):
    if test==True:
        columns = ['Identifiant_Produit','Description','Libelle','Marque','prix']
    else:
        columns = ['Identifiant_Produit','Categorie1','Categorie2','Categorie3','Description','Libelle','Marque','Produit_Cdiscount','prix']
    return columns

def normalize_txt(txt):
    # remove html stuff
    txt = BeautifulSoup(txt,from_encoding='utf-8').get_text()
    # lower case
    txt = txt.lower()
    # special escaping character '...'
    txt = txt.replace(u'\u2026','.')
    txt = txt.replace(u'\u00a0',' ')
    # remove accent btw
    txt = unicodedata.normalize('NFD', txt).encode('ascii', 'ignore')
    #txt = unidecode(txt)
    # remove non alphanumeric char
    txt = re.sub('[^a-z_]', ' ', txt)
    # remove french stop words
    tokens = [w for w in txt.split() if (len(w)>2) and (w not in stopwords)]
    # french stemming
    tokens = stemmer.stemWords(tokens)
    return ' '.join(tokens)

def normalize_price(price):
    if (price<0) or (price>100):
        price = 0
    return price

def normalize_file(fname,header,nrows = None):
    columns = {k:v for v,k in enumerate(header)}
    ofname = fname.split('.')[0]+'_normed.'+fname.split('.')[1]
    ff = open(ofname,'w')
    start_time = time.time()
    counter = 0
    for line in open(fname):
        if line.startswith('Identifiant_Produit'):
            continue
        di = columns['Description']
        li = columns['Libelle']
        mi = columns['Marque']
        pi = columns['prix']
        if counter%1000 == 0:
            print fname,': lines=',counter,'time=',int(time.time() - start_time),'s'
        ls = line.split(';')
        # marque normalization
        txt = ls[mi]
        txt = re.sub('[^a-zA-Z0-9]', '_', txt).lower()
        ls[mi] = txt
        #
        # description normalization
        ls[di] = normalize_txt(ls[di])
        #
        # libelle normalization
        ls[li] = normalize_txt(ls[li])
        #
        # prix normalization
        ls[pi] = str(normalize_price(float(ls[pi].strip())))
        line = ';'.join(ls)
        ff.write(line+'\n')
        counter += 1
        if (nrows is not None) and (counter>=nrows):
            break
    ff.close()
    return

class iterText(object):
    def __init__(self, df):
        """
        Yield each document in turn, as a text.
        """
        self.df = df
    
    def __iter__(self):
        for row_index, row in self.df.iterrows():
            if (row_index>0) and (row_index%10000)==0:
                print row_index,'/',len(self.df)
            txt = ' '.join([row.Marque]*3+[row.Libelle]*2+[row.Description])
            yield txt
    
    def __len__(self):
        return len(self.df)

class MarisaTfidfVectorizer(TfidfVectorizer):
    def fit_transform(self, raw_documents, y=None):
        super(MarisaTfidfVectorizer, self).fit_transform(raw_documents)
        self._freeze_vocabulary()
        return super(MarisaTfidfVectorizer, self).fit_transform(raw_documents, y)
    def fit(self, raw_documents, y=None):
        super(MarisaTfidfVectorizer, self).fit(raw_documents)
        self._freeze_vocabulary()
        return super(MarisaTfidfVectorizer, self).fit(raw_documents, y)
    def _freeze_vocabulary(self, X=None):
        if not self.fixed_vocabulary_:
            self.vocabulary_ = marisa_trie.Trie(six.iterkeys(self.vocabulary_))
            self.fixed_vocabulary_ = True
            del self.stop_words_
