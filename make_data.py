import pandas as pd

df_remove = pd.read_csv('./michele_data.csv',low_memory=False)
remove_codes = list(df_remove['Code searched'])
df_master = pd.read_csv('./MLAProductExport-25-08-2023.csv',low_memory=False)

uxref = df_master.loc[df_master['Product Name']=='UNCONFIRMED_XREF']
out = uxref.loc[~uxref['Code'].isin(remove_codes)] #returns boolean series so negate output to get is not isin

drop_col = set(out.columns) - set(['Code','Product Name','Category'])
out = out.drop(list(drop_col), axis=1)
out.to_csv('data.csv',index=False)


