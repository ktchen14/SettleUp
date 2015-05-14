import csv
import re

card = re.compile(r'Card \(([0-9]{4})\)')

mycsv = []
with open('cleaned.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['Categories'] = row['Categories'].split(', ')
        if 'NYC' not in row['Categories']:
            if 'For Both of Us' in row['Categories'] or 'For Kaiting' in row['Categories'] or 'For Melanie' in row['Categories']:
                mycsv.append(row)
            else:
                raise ValueError('Data Steward made a mistake')
for line in mycsv:
    if card.match(line['Payment Type']):
        mo = card.match(line['Payment Type'])
        line['Payment Type'] = mo.group(1)
    elif 'By Melanie' in line['Categories'] or 'By Kaiting' in line['Categories']:
        pass
    else:
        raise ValueError('Batch rejected due to no payer label or cc number')
for line in mycsv:
    print line
