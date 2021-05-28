import pandas as pd
import numpy as np
import pickle
import partition
import os
import socket
import re 
import whois
import requests
import math

from urllib.parse import urlparse, parse_qs
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from ip2geotools.databases.noncommercial import DbIpCity
from tld import get_tld
from bs4 import BeautifulSoup
import string
# from org.jsoup import Jsoup

### Helping functions
# Convert a multiple categorical to ONE-HOT 
def to_one_hot(df, col:str, exclude:set=None):
    if exclude is None:
        exclude = set()

    cs = set(df[col])
    for c in cs - exclude:
        df[c.lower()] = df[col] == c
        df[c.lower()] = df[c.lower()].astype(int)
    del df[col]

# Convert a binary categorical to ONE-HOT
def to_num(df, new_name:str, col_name:str, value:str):
    df[new_name] = df[col_name] == value
    df[new_name] = df[new_name].astype(int)

# Normalise column
def norm_col(df, col:str):
    max_val = max(df[col])
    df[col] = df[col] / max_val
    df[col] = df[col].astype(int)

# URL preprocessing
def get_parsed_url (row):
    return urlparse(row.url)

def get_body_len (row):
    parsed = get_parsed_url(row)
    return len(parsed.netloc)

def get_num_args (row):
    parsed = get_parsed_url(row)
    params = parse_qs(parsed.query)
    path_components = list(filter(bool, parsed.path.split('/')))
    return len(path_components) + len(list(params))

# Entropy
def get_entropy(row):
    string = row.url.strip()
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    entropy = sum([(p * math.log(p) / math.log(2.0)) for p in prob])
    return entropy

# URL path length
def get_path_len (row):
    parsed = get_parsed_url(row)
    return len(parsed.path)

# URL letters length
def get_letter_count (row):
    letters = 0
    for i in row.url:
        if i.isalpha():
            letters = letters + 1
    return letters

# URL digits length (numbers and symbols)
def get_digits_len (row):
    digits = 0 
    for i in row.url:
        if i.isnumeric():
            digits = digits + 1
        if i in string.punctuation:
            digits = digits + 1
    return digits

def is_http (row):
    parsed = get_parsed_url(row)
    return parsed.scheme


class DFPreprocessing: 
    def __init__(self, data_name:str, btrunc:int, atrunc:int):
        self.df = pd.read_csv(data_name)
        self.df = self.df[['url','ip_add','geo_loc','url_len','js_len','js_obf_len','tld','who_is','https','content','label']]
        self.df = self.df.truncate(before=btrunc, after=atrunc)
    
    def replace_countries (self):
        self.df.replace(to_replace='Congo Republic', value='Congo', inplace=True)
        self.df.replace(to_replace='DR Congo', value='Congo', inplace=True)
        self.df.replace(to_replace='U.S. Virgin Islands', value='United States', inplace=True)
        self.df.replace(to_replace='Åland', value='Unknown', inplace=True)
        self.df.replace(to_replace='Sint Maarten', value='Unknown', inplace=True)
        self.df.replace(to_replace='Bonaire, Sint Eustatius, and Saba', value='Unknown', inplace=True)
        self.df.replace(to_replace='Vatican City', value='Unknown', inplace=True)
        self.df.replace(to_replace='Kosovo', value='Unknown', inplace=True)
        self.df.replace(to_replace='East Timor', value='Unknown', inplace=True)
        self.df.replace(to_replace='St Kitts and Nevis', value='Unknown', inplace=True)
        self.df.replace(to_replace='French Southern Territories', value='Unknown', inplace=True)
        self.df.replace(to_replace='Saint Helena', value='Unknown', inplace=True)
        self.df.replace(to_replace='Antarctica', value='Unknown', inplace=True)

    def country2continent (self, row):
        if row.geo_loc != 'Unknown':
            cn_a2_code = country_name_to_country_alpha2(row.geo_loc)
            cn_continent = country_alpha2_to_continent_code(cn_a2_code)
            return cn_continent
        return row.geo_loc

    def sep(self):
        x = self.df.copy()
        del x['label']
        y = pd.DataFrame(self.df['label'])
        return x, y


    def preprocess (self, save_name):
        self.df['url_body_len'] = self.df.apply(get_body_len, axis=1)

        self.df['url_num_args'] = self.df.apply(get_num_args, axis=1)

        self.df['entropy'] = self.df.apply(get_entropy, axis=1)

        self.df['url_path_len'] = self.df.apply(get_path_len, axis=1)

        self.df['url_letters_len'] = self.df.apply(get_letter_count, axis=1)

        self.df['url_digit_len'] = self.df.apply(get_digits_len, axis=1)

        del self.df['url'], self.df['ip_add']

        self.replace_countries()

        self.df['con_loc'] = self.df.apply(self.country2continent, axis=1)
        del self.df['geo_loc']

        to_one_hot(self.df, 'con_loc', {'?'})

        for col in self.df.columns:
            if col == 'unknown':
                del self.df['unknown']

        to_num(self.df, 'is_com', 'tld', 'com')
        del self.df['tld']

        to_num(self.df, 'who_is', 'who_is', 'complete')

        to_num(self.df, 'https', 'https', 'yes')

        to_num(self.df, 'label', 'label', 'bad')

        del self.df['content'], self.df['js_obf_len']

        # Normalize every column
        for col in self.df:
            self.df[col] = self.df[col].astype(float)
            self.df[col] = (self.df[col] / max(abs(self.df[col])))
        self.df = self.df.fillna(0.0)
        
        print(self.df.columns)
        print(self.df.head())

        # Separate x and y values
        x, y = self.sep()

        # Export data
        pair = x, y

        dataset_name = '../Datasets/' + save_name
        with open(dataset_name, 'wb') as f:
            pickle.dump(pair, f)



class SamplePreprocessing:
    def __init__(self, url:str):
        self.url = url
    
    def get_content(self):
        try:
            r = requests.get(self.url)
            soup = BeautifulSoup(r.content, 'html.parser')
            [s.extract() for s in soup(['iframe', 'script', 'style'])]
            raw_text = soup.text
            raw_text.translate(str.maketrans('', '', string.punctuation))
            raw_text = raw_text.lower()
            raw_text = raw_text.replace("\n", "")
            return raw_text
        except:
            return "ERROR"

    def get_ip(self):
        p_url = urlparse(self.url).netloc
        return socket.gethostbyname(p_url) 

    def get_js_len_inKB(self):
        if self.content == "ERROR":
            return 1000
        js = ''.join(str(j) for j in self.content)
        return len(js.encode('utf-8'))/1000
        
    def get_whois (self):
        query = whois.whois(self.url)
        domain = query.registrar
        if len(str(domain)) > 1 :
            return 0.0
        else: 
            return 1.0
    
    def country2continent (self, country):
        if country != 'Unknown':
            return country_alpha2_to_continent_code(country)
        return country

    def get_continent(self):
        response = DbIpCity.get(self.ip, api_key='free')
        return self.country2continent(response.country)

    def preprocess(self):
        self.content = self.get_content() 
        self.ip = self.get_ip()

        # Create dataframe from the recieved data
        self.df = pd.DataFrame(data={'url': [self.url], 'ip_add': [self.ip], 'content': [self.content]})
        print(self.url)
        print(self.ip)
        # get url_length 
        self.df['url_len'] = self.df['url'].str.len()

        # Get js_length
        self.df['js_len'] = self.get_js_len_inKB()

        # Get who_is attribute
        self.df['who_is'] = self.get_whois()

        # Get if the URL is http or https
        self.df['https'] = self.df.apply(is_http, axis=1)

        to_num(self.df, 'https', 'https', 'https')

        # Get the URL body length
        self.df['url_body_len'] = self.df.apply(get_body_len, axis=1)

        self.df['url_num_args'] = self.df.apply(get_num_args, axis=1)

        self.df['entropy'] = self.df.apply(get_entropy, axis=1)

        self.df['url_path_len'] = self.df.apply(get_path_len, axis=1)

        self.df['url_letters_len'] = self.df.apply(get_letter_count, axis=1)

        self.df['url_digit_len'] = self.df.apply(get_digits_len, axis=1)

        del self.df['url']

        # Get continent from URL
        con_loc = self.get_continent()
        self.df['con_loc'] = con_loc

        for i in ['na', 'eu', 'oc', 'af', 'as', 'sa']:
            self.df[i] = 0

        to_one_hot(self.df, 'con_loc', {'?'})

        # Get if the Top Level Domain of the URL is .com or not
        self.df['tld'] = get_tld(self.url)
        to_num(self.df, 'is_com', 'tld', 'com')

        del self.df['tld']

        # Delete unused DF columns
        del self.df['ip_add'], self.df['content']

        # Normalize every column
        for col in self.df: 
            self.df[col] = self.df[col].astype(float)
            if col == 'js_len':
                self.df[col] = np.minimum(self.df[col] / 855, 1)
            elif col == 'url_len':
                self.df[col] = np.minimum(self.df[col] / 721, 1)
            elif col == 'url_body_len':
                self.df[col] = np.minimum(self.df[col] / 71, 1)
            elif col == 'url_num_args':
                self.df[col] = np.minimum(self.df[col] / 20, 1)
        
        self.df = self.df.fillna(0.0)
        self.df = self.df.to_numpy()
        print(self.df[0])
        return self.df
