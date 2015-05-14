import csv
from decimal import Decimal
from datetime import datetime
import re

card = re.compile(r'Card \(([0-9]{4})\)')

def cleanse_amount(record):
    return Decimal(record['Total (USD)'])

def cleanse_merchant_name(record):
    if not record['Store']:
        return None
    else:
        return record['Store']

def cleanse_cc(record):
    if card.match(record['Payment Type']):
        mo = card.match(record['Payment Type'])
        record['Payment Type'] = mo.group(1)
    elif 'By Melanie' in record['Categories']:
        return 'MELA'
    elif 'By Kaiting' in record['Categories']:
        return 'KMAN'

def cleanse_remote_id(record):
    return record['Link'].split('/')[-1]

def cleanse_owner(record):
    for label in record['Categories']:
        if label == 'For Melanie':
            return 'Melanie Plageman'
        elif label == 'For Kaiting':
            return 'Kaiting Chen'
        elif label == 'For Both of Us':
            return None

def cleanse_transaction_date(record):
    if not record['Date']:
        return None
    else:
        return datetime.strptime(record['Date'], '%b %d, %Y').date()

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
    elif 'By Melanie' in line['Categories'] or 'By Kaiting' in line['Categories']:
        pass
    else:
        raise ValueError('Batch rejected due to no payer label or cc number')
for line in mycsv:
    cleanse_merchant_name(line)
    cleanse_cc(line)
    cleanse_amount(line)
    cleanse_remote_id(line)
    cleanse_owner(line)
    cleanse_transaction_date(line)
