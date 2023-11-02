import michele
from os import listdir
import pandas as pd

def find_csv_names(path):
    files = listdir(path)
    return([file for file in files if file.endswith(".csv")])

def find_last_code():
    path="/home/ben/Documents/MLA_Dev/Scrape_01_23/output_data"
    last_file_num = max([int(x[x.rfind('_')+1:x.rfind('.')]) for x in find_csv_names(path)])
    file_path = f'./output_data/Michele_scraped_data_{last_file_num}.csv'
    df = pd.read_csv(file_path)
    return(df['Code searched'].iloc[-1])

def find_last_error():
    with open('./errors.log') as f:
        for line in f:
            pass
        return(line[line.find('code')+5:-1])

df = pd.read_csv('./data.csv',low_memory=False) #load once and grab codes
while True:
    checks=[find_last_error(),find_last_code()]
    codes = df['Code']
    next_index = max([list(codes).index(x) for x in checks])
    codes=codes[next_index:]
    if len(codes)<2:
        break
    try:
        michele.Scrape_Michele(codes,100)
    except:
        print('Restarting')

print('Execution finished')
