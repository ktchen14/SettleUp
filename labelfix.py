import collections
import csv
from decimal import Decimal
from datetime import datetime
import re
import psycopg2

# compile regex to match credit card field
card = re.compile(r'Card \(([0-9]{4})\)')

# create named tuple which is all of the target fields
Transaction = collections.namedtuple('Transaction', [
    'amount', 'merchant_name', 'cc', 'owner', 'remote_id', 'transaction_date'
])

mycsv = []
with open('cleaned.csv') as f:
    reader = csv.DictReader(f)
    for record in reader:
        # for the string value of the Categories field, create a list of strings split at commas
        record['Categories'] = record['Categories'].split(', ')
        # only add the records that don't include NYC in the list of Categories
        if 'NYC' not in record['Categories']:
            mycsv.append(record)

def cleanse_amount(record):
    if not record['Total (USD)']:
        raise ValueError('No transaction amount recorded')
    else:
        return Decimal(record['Total (USD)'])

def cleanse_merchant_name(record):
    if not record['Store']:
        return None
    else:
        return record['Store']

# for the value of the Payment Type field, if it is not either a cc number or a payer label, then raise an error                
def cleanse_cc(record):
    if card.match(record['Payment Type']):
        mo = card.match(record['Payment Type'])
        return mo.group(1)
    elif 'By Melanie' in record['Categories']:
        return 'MELA'
    elif 'By Kaiting' in record['Categories']:
        return 'KMAN'
    else:
        raise ValueError('Batch rejected due to no payer label or cc number')
        
def cleanse_remote_id(record):
    if not record['Link']:
        raise ValueError('No pdf link recorded')
    else:
        return record['Link'].split('/')[-1]

# get owner labels from Categories and throw error if no owner label
def cleanse_owner(record):
    if 'For Melanie' in record['Categories']:
        return 'Melanie Plageman'
    elif 'For Kaiting' in record['Categories']:
        return 'Kaiting Chen'
    elif 'For Both of Us' in record['Categories']:
        return None
    else:
        raise ValueError('Data Steward made a mistake')

def cleanse_transaction_date(record):
    if not record['Date']:
        return None
    else:
        return datetime.strptime(record['Date'], '%b %d, %Y').date()

conn = psycopg2.connect(
        host='ec2-107-22-187-89.compute-1.amazonaws.com',
        database='dbtrl58pa0ipp6',
        user='rpvalfmhbpbsml')
cursor = conn.cursor()

for line in mycsv:
    t = Transaction(
        merchant_name = cleanse_merchant_name(line),
        cc = cleanse_cc(line),
        amount = cleanse_amount(line),
        remote_id = cleanse_remote_id(line),
        owner = cleanse_owner(line),
        transaction_date = cleanse_transaction_date(line)
    )
    cursor.execute(
        'INSERT INTO transactions (merchant_name, cc, amount, remote_id, owner, transaction_date) VALUES (%s, %s, %s, %s, %s, %s);',
        (t.merchant_name, t.cc, t.amount, t.remote_id, t.owner, t.transaction_date)
    )

conn.commit()
conn.close()
