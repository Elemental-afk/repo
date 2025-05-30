import pandas as pd
import numpy as np
from numpy import linalg as LA
from sklearn.decomposition import TruncatedSVD
import re
import os
import pyarrow


CSV_FILE = "assets/results.csv"

def clear_text(text):
    if type(text) != str:
        text = str(text)
    text = text.replace("\n", "") 
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"[:/–„”'*!?.,()[\]]", " ", text)
    text = text.lower()
    return text

def make_terms_list(df):
    terms = df.str.split(r"\ \b", expand=True).melt().drop_duplicates(subset=['value'])
    terms = pd.DataFrame(index=terms["value"])
    return terms

def create_bag_by_doc(terms, docs):
    termbydoc = terms.copy()
    if type(docs) != str:
        n = len(docs)
    else:
        n = 1
    for i in range(n):
        if type(docs) != str:
            text = docs.iloc[i]
        else:
            text = docs
        words = text.split()
        counts = pd.Series(words, name='value').value_counts()

        colname = 'd' + str(i)
        termbydoc[colname] = 0
        termbydoc[colname] = termbydoc.index.map(counts).fillna(0).astype(int)
           
    return termbydoc


def idf_create(bag):
    N = bag.shape[1]
    nws = bag.astype(bool).sum(axis=1)
    idf_weights = np.log(N / nws)
    idf_bag = bag.mul(idf_weights, axis=0)
    idf_bag.fillna(value = 0, inplace = True)

    return idf_bag

def dumbsearch(ask, bag, howmanyresults, terms):
    q = create_bag_by_doc(terms, ask).to_numpy()
    similarities = []
    for i in range(len(bag.columns)):
        d = bag["d" + str(i)].to_numpy()
        cos = (q.T @ d) / (0.000001 + LA.norm(q) * LA.norm(d))
        similarities.append((cos[0], i))

    similarities.sort(reverse=True)
    return similarities[:howmanyresults]

def dumbsearch_with_vec(ask, bag, howmanyresults, terms):
    q = create_bag_by_doc(terms, ask).to_numpy()
    q_norm = q / LA.norm(q)

    if not isinstance(bag, np.ndarray):
        A = bag.to_numpy()
    else:
        A = bag
    
    A_norm = A / (LA.norm(A, axis=1, keepdims=True) + 0.000001)
    similarities = q_norm.T @ A_norm

    res_sim = []
    for i in range(similarities.shape[1]):
        res_sim.append((similarities[0, i], i))
    

    res_sim.sort(reverse=True)
    return res_sim[:howmanyresults]

def smartsearch(ask, bag, k, terms,howmanyresults):
    svd = TruncatedSVD(n_components=k, algorithm='randomized')
    print("Computing SVD...")
    U_k = svd.fit_transform(bag)
    S_k = svd.singular_values_
    Vh_k = svd.components_
    print("SVD computation finished.")
    A_k = U_k @ np.diag(S_k) @ Vh_k
    print("Computing similarities...")
    return dumbsearch_with_vec(ask, A_k, howmanyresults, terms)

def create_results(results, df):
    output = []
    
    for doc in results:
        doc_index = doc[1] 
        doc_data = df.iloc[doc_index]
        
        result = {
            'title': doc_data['title'],
            'url': doc_data['url'],
            'preview': doc_data['text'][:150] + '...'
        }
        
        output.append(result)

    print("Results:")
    print(output)
    return output


def search(query, idf, searchtype, samplek, howmanyresults):
    df = pd.read_csv(CSV_FILE)
    df_new = df['text'].apply(lambda x: clear_text(x))
    query = clear_text(query)

    terms_path = "assets/terms.parquet"
    if os.path.exists(terms_path):
        terms = pd.read_parquet(terms_path)
    else:
        terms = make_terms_list(df_new)
        terms.to_parquet(terms_path, engine='pyarrow')
    
    bag_path = "assets/bag.parquet"
    if os.path.exists(bag_path):
        bag = pd.read_parquet(bag_path)
    else:
        bag = create_bag_by_doc(terms, df_new)
        bag.to_parquet(bag_path, engine='pyarrow')
    
    if idf:
        idf_path = "assets/idf.parquet"
        if os.path.exists(idf_path):
            idf = pd.read_parquet(idf_path)
        else:
            idf = idf_create(bag)
            idf.to_parquet(idf_path, engine='pyarrow')
    else:
        idf = bag

    if searchtype == "dumb":
        results = dumbsearch(query, idf, howmanyresults, terms)
    elif searchtype == "dumbvec":
        results = dumbsearch_with_vec(query, idf, howmanyresults, terms)
    elif searchtype == "smart":
        results = smartsearch(query, idf, samplek, terms, howmanyresults)

    return create_results(results, df)