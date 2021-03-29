import os

import requests
import pandas as pd
from pandas import read_csv
import time
from datetime import datetime
import json

from biothings.utils.common import open_anyfile
from biothings import config
logger = config.logger

import requests_cache

expire_after = datetime.timedelta(days=7)

requests_cache.install_cache('litcovidtopics_cache',expire_after=expire_after)
logger.debug("requests_cache: %s", requests_cache.get_cache().responses.filename)

        
def get_pmids(res):
    data=[]
    litcovid_data = res.text.split('\n')[34:]
    for line in litcovid_data:
        if line.startswith('#') or line.startswith('p'):
            continue
        if len(line.strip())<5:
            continue
        data.append('pmid'+line.split('\t')[0])
    return(data)


def get_topics():
    topics = {'Mechanism':'Mechanism',
              'Transmission':'Transmission',
              'Diagnosis':'Diagnosis',
              'Treatment':'Treatment',
              'Prevention':'Prevention',
              'Case%20Report':'Case Descriptions',
              'Epidemic%20Forecasting':'Forecasting'}
    pmid_dict = {}
    for topic in topics.keys():
        res = requests.get('https://www.ncbi.nlm.nih.gov/research/coronavirus-api/export/tsv?filters=%7B%22topics%22%3A%5B%22'+topic+'%22%5D%7D')
        data = get_pmids(res)
        pmid_dict[topics[topic]]=data
        time.sleep(1)
    return(pmid_dict)


def transform_dict(pmid_dict):
    new_dict = {}
    for eachkey in pmid_dict.keys():
        pmidlist = pmid_dict[eachkey]
        tmpdf = pd.DataFrame(pmidlist)
        tmpdf['topicCategory']=eachkey
        tmpdf.reset_index().rename(columns={'0':'_id'},)
        new_dict[eachkey]=tmpdf
    return(new_dict)


def merge_results(pmid_dict):
    allresults = pd.concat((pmid_dict.values()), ignore_index=True)
    allresults.rename(columns={0:"_id"},inplace=True)
    return(allresults)


def clean_results(allresults):
    counts = allresults.groupby('_id').size().reset_index(name='counts')
    duplicates = counts.loc[counts['counts']>1]
    singles = counts.loc[counts['counts']==1]
    dupids = duplicates['_id'].unique().tolist()
    tmplist = []
    for eachid in dupids:
        catlist = allresults['topicCategory'].loc[allresults['_id']==eachid].tolist()
        tmplist.append({'_id':eachid,'topicCategory':catlist})
    tmpdf = pd.DataFrame(tmplist)  
    tmpsingledf = allresults[['_id','topicCategory']].loc[allresults['_id'].isin(singles['_id'].tolist())]
    idlist = tmpsingledf['_id'].tolist()
    catlist = tmpsingledf['topicCategory'].tolist()
    cattycat = [[x] for x in catlist]
    list_of_tuples = list(zip(idlist,cattycat))
    singledf = pd.DataFrame(list_of_tuples, columns = ['_id', 'topicCategory']) 
    cleanresults = pd.concat((tmpdf,singledf),ignore_index=True)
    return(cleanresults)  


def load_annotations():
    pmid_dict = get_topics()
    clean_dict = transform_dict(pmid_dict)
    allresults = merge_results(clean_dict)
    cleantopics = clean_results(allresults)
    for doc in json.loads(cleantopics.to_json(orient="records")):
        yield(doc)