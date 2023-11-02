#!/usr/bin/env python3.9
import hifi                                                #<----------- change this
import os
import pandas as pd
from joblib import Parallel, delayed

def find_csv_names(path):
    files = os.listdir(path)
    return([file for file in files if file.endswith(".csv")])

def split_df(df,n):
    return([df[i:i+n] for i in range(0,len(df),n)])

def number_thread():
    path = "./threaded_output_data"
    taken = [int(file.replace('.txt','')) for file in os.listdir(path) if file.endswith(".txt")]
    available = [x for x in list(range(system_threads)) if x not in taken]
    if available == []:
        return(None)
    thread_num=min(available)
    file = path+f'/{thread_num}.txt'
    with open(file, 'w') as f:
        f.write('Thread running')
    return(thread_num)

def safe_index(codes,code):
    try:
        index = codes.index(code)
    except ValueError: #last error/searched not in codes as has been removed or in different code block
        index = 0
    return(index)

def update_data_csv(threads):
    rel_dir = './threaded_output_data'
    main_df = pd.read_csv('./data.csv',low_memory=False) #load once and grab codes
    for i in range(threads):
        path = rel_dir + f'/thread_{i}'
        for csv in find_csv_names(path):
            df = pd.read_csv(csv)
            codes = list(df['Code searched'])
            main_df = main_df[~main_df['Code'].isin(codes)]
    return(main_df) 

def Run(codes):
    thread_num = None
    while thread_num == None:
        thread_num = number_thread()
    exit_code = "EMPTCODE" #will throw ValueError for safe_index so will default to 0 on first run
    while True:
        next_index = max([safe_index(list(codes),exit_code)]+[0]) 
        codes=codes[next_index:]
        try:
            print(f'Executing code on thread: {thread_num}')
            exit_code = hifi.Scrape_Hifi(codes,thread_num)     #exit_code will either be a code that we failed on or "Complete"  
            if exit_code == "Complete":
                break
        except Exception as error:
            print(f"An exception occurred on thread {thread_num}:", type(error).__name__, "–", error)
    
    os.remove(f"./threaded_output_data/{thread_num}.txt") #free up thread number
    return('Complete')

def setup(threads):
    #remove previous txt files
    txt_files = ['./threaded_output_data/'+file for file in os.listdir('./threaded_output_data') if file.endswith(".txt")]
    for file in txt_files:
        os.remove(file)

    #ensure enough directories for given thread number exists
    parent_dir = './threaded_output_data/'
    for i in range(0,threads):
        child_dir = f'thread_{i}'
        path = os.path.join(parent_dir,child_dir)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
    
    #ensure logs directory exists
    try:
        os.mkdir("./logs")
    except FileExistsError:
        pass

def read_threads():
    with open('thread_count.txt') as f:
        thread_count = f.readlines()[0]
        thread_count = int(thread_count)
    return(thread_count)

system_threads = read_threads()
setup(system_threads)
df = update_data_csv(system_threads) #input number of threads
code_chunks = split_df(df['Code'],2000)
Parallel(n_jobs = system_threads)(delayed(Run)(codes) for codes in code_chunks)

