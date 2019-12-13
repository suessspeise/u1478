


# convert new one from ods
#soffice --headless --convert-to csv U1478_mastertable.ods
ssconvert ../data/pollen/U1478_mastertable.ods ../data/pollen/U1478.csv
# make plots
python3 plot.py

#curl -T 'picklist.html' ftp://camposcampos.de/uni --user u22004:'gogNar1<Uk2Woant'