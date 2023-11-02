#!/bin/bash

#loop through directories and for each one get all csvs and combine with removing 
#the header. next push to a file called thread_x_combined.csv where we use %/ to remove the directory / 
#then we combine all csvs again into one final one and remove out interim csvs for each thread directory

for d in */
do
    cat $d/*.csv | awk '!a[$0]++' > "${d%/}_combined.csv"
done

cat *.csv | awk '!a[$0]++' > scrape_data.csv
rm *combined.csv

