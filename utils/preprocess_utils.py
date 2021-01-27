# %%
import pandas as pd
import numpy as np
import email
from ast import literal_eval
import time

# %%
import sys
#sys.path.append('/home/trisha/NLP_enron_email/venv/lib/python3.7/site-packages')

# %%
from fuzzywuzzy import fuzz, process


# %%
class EmailHeaderAndBodySeparation:
    def __init__(self):
        self.df = None
        self.headerlist = None
        
    def __insert_value__(self,dictionary,key,value):
        if key in dictionary:
            values = dictionary.get(key)
            values.append(value)
            dictionary[key] = values
        else:
            dictionary[key] = [value]
        return dictionary    
    def get_headers(self):
        headers = {}
        messages = self.df["message"]
        for message in messages:
            e = email.message_from_string(message)
            for item in self.headerlist:
                header = e.get(item)
                self.__insert_value__(dictionary = headers, key = item, value = header) 
        print("Successfully retrieved header information!")
        return headers
    def get_messages(self):
        messages = []
        for item in self.df["message"]:
            # Return a message object structure from a string
            e = email.message_from_string(item)    
            # get message body  
            message_body = e.get_payload()
            message_body = message_body.lower()
            messages.append(message_body)
        print("Successfully retrieved message body from e-mails!")
        return messages
    def sep_headers_n_body(self,df, headernames):
        self.df = df
        self.headerlist = headernames
        
        headers = self.get_headers()
        msg_body = self.get_messages()
        self.df["Message body"] = msg_body
        for label in self.headerlist:
            df_new = pd.DataFrame(headers[label], columns = [label])
            if label not in self.df.columns:
                self.df = pd.concat([self.df, df_new], axis = 1)
        return self.df

# %%
def preprocess_folder(folder,splitter):
    if folder is None:
        items = []
        return items.append(np.nan)
    else:
        folder = folder.replace('"','')
        folder = folder.replace("'","")
        return folder.split(splitter)

# %%
def preprocess_folder_get_last(folder,splitter,itemnumber):
    if folder is None:
        items = []
        return items.append(np.nan)
    else:
        folder = folder.replace('"','')
        folder = folder.replace("'","")
        try:
            return folder.split(splitter)[itemnumber]
        except:
            return 'None'

# %%
def extract_company(email_addr, BOOL_as_list = False):
    #returns all company names in the string separated by commas
    if BOOL_as_list:
        listadress = email_addr.split(',')
        listcompanies = [email.split('@')[-1].split('.')[0] for email in listadress]
        return list(set(listcompanies))
    #returns assuming only one company name
    else:
        return email_addr.split('@')[-1].split('.')[0]

# %%


# %%
class AssignLabeltoEmail:
    def __init__(self):
        self.df = None
        self.column = None
    ##replace any characters which are not letter including underscore, multiple spaces, keep '-'. Then replce
    #single characters. then trailing, multiple and leading spaces
    def preprocess_text(self):
        self.df[self.column] = self.df[self.column].fillna("None").str.lower().str.\
replace("([^\\a-z-]+)|_+|\.+|([0-9]+)|\s+", " ").str.replace(r"\b[a-z-]\b|\s+", " ").str.strip()
        
        return 
        
    def replace_items(self):
        ##replace similar folder names
        rep_dic = {'sent items':'sent',
           'sent email':'sent','sent mail':'sent',
           'deleted items':'deleted','notes inbox':'inbox',
           'hr':'human resources',
           '':'None',
           'california - working group': 'california',
             'california issues':'california',
          'federal legis':'federal legislation',
           'ge general':'general',
             'general stuff':'general',
           'hpl customers':'hpl',
           'junk file':'junk',
         'legal agreements':'legal',
           'misc':'miscellaneous',
           'old email':'old messages',
         'old inbox':'old messages', 
         'personal mail':'personal',
         'personal stuff':'personal',
         'personalfolder':'personal',
           'saved-':'savedmail'
          }
        
        self.df[self.column] = self.df[self.column].replace(rep_dic)
        return
    
    #get only unique words from a list
    def get_unique_words(self, word, listofwords, cutoff=80):
        for item in listofwords:
            if fuzz.ratio(word,item)>=cutoff:
                #print(word,item,fuzz.ratio(word,item))
                return item
            
    #get most similar word from a list to a passed word
    def find_similar_word_from_list(self, word, listofwords, cutoff = 70):
        try:
            return list(process.extractOne(word,listofwords, score_cutoff=cutoff))[0]
        except:
            return 'None'
        
    def get_labels(self, df, column, new_column):
        self.df = df
        self.column = column
        
        self.preprocess_text()
        self.replace_items()
        
        #get frequently occurring folder names
        listfromfoldernames = self.df[self.column].value_counts().index[:200].tolist()
        
        #compbination of most 100 frquently occuriing folder items and file items
        #sort by alphabetical order
        compare = sorted(list(set(listfromfoldernames)))
        #drop items of length less than 1 for eg '/''
        compare = list(filter (lambda item: len(item)>1, compare))
        
        
        #get unique entries from the list
        comparefinal = list(set(\
                        list(\
                    map(\
                        lambda x:self.get_unique_words(compare[x],compare), range(0,len(compare))\
                       )\
                   )\
                       ))
        print("Length of unique classes:",len(comparefinal),"Classes :",comparefinal)

        #create class for eack email finding similarity of folder items with list of curated items
        self.df[new_column] = self.df[self.column].apply(lambda x: self.find_similar_word_from_list(x,comparefinal,70))
        
        return self.df

