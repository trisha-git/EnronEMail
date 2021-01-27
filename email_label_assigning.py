# ---
# jupyter:
#   jupytext:
#     formats: ipynb,md,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: venv
#     language: python
#     name: venv
# ---

# +
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
#import email
#from ast import literal_eval
import time


import sys
sys.path.append("utils/")
import preprocess_utils 
#sys.path.append('/home/trisha/NLP_enron_email/venv/lib/python3.7/site-packages')
import plotly.express as px
from fuzzywuzzy import fuzz, process

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))


# +

# %load_ext autoreload
# %autoreload 2

# +
def read_data(datafilepath, chunksize=1000, BOOL_all_data = False):
    #to read entire file
    if BOOL_all_data:
        chunk = pd.read_csv(datafilepath)
        return chunk
    else:
        chunk = pd.read_csv(datafilepath,chunksize=chunksize)
        raw_data = next(chunk)
        return raw_data
    
datafilepath = 'emails.csv'
#to read entire file set BOOL_all_data =True
chunk = read_data(datafilepath)
# -

header_names = ["Date", "Subject", "X-Folder", "X-From", "X-To","X-Origin", "X-cc","From","To"] 
mailheadbody = preprocess_utils.EmailHeaderAndBodySeparation()
emails = mailheadbody.sep_headers_n_body(chunk, header_names)

# +
# Convert date column to datetime 
emails["Date"] = pd.to_datetime(emails["Date"])
##get folder items in list format
emails["X-Folder items"] = emails["X-Folder"].apply(lambda x: preprocess_utils.preprocess_folder(x,'\\'))
emails["X-Folder last item"] = emails["X-Folder"].apply(lambda x: preprocess_utils.preprocess_folder_get_last(x,'\\',-1))

##get file items in list format
emails["File items"] = emails["file"].apply(lambda x: preprocess_utils.preprocess_folder(x,'/'))
emails["File second item"] = emails["file"].apply(lambda x: preprocess_utils.preprocess_folder_get_last(x,'/',1))

##get company names from email address
emails["To company"] = emails["To"].fillna('None@None.com').apply(lambda x: preprocess_utils.extract_company(x))
emails["From company"] = emails["From"].fillna('None@None.com').apply(lambda x: preprocess_utils.extract_company(x))




# +
labelassigner = preprocess_utils.AssignLabeltoEmail()

emails = labelassigner.get_labels(emails,"X-Folder last item","X-Folder class")


# +
#emails.to_csv("emails_processed_folder_header.csv",index=False,sep="|")
# -


