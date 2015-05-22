import re
import collections
from datetime import datetime
from decimal import Decimal

# compile regex for credit card
card = re.compile(r'Card \(([0-9]{4})\)')

# create named tuple which is all of the target fields
Transaction = collections.namedtuple('Transaction', [
    'amount', 'merchant_name', 'cc', 'owner', 'remote_id', 'transaction_date'
])

def check_label(labels, labelslist):
    categories = set(labelslist)
    intersection = categories.intersection(labels)
    if len(intersection) == 1: return tuple(intersection)[0]
    else: raise ValueError('Incorrect labels')

def record_to_transaction(record):
    for field in ['Total (USD)', 'Link', 'Date', 'Store']:
        if not record[field]: raise ValueError('Missing required value')

    transaction_date = datetime.strptime(record['Date'], '%b %d, %Y').date()

    result = card.match(record['Payment Type'])
    if result:
        cc = result.group(1)
    else:
        payer_labels = {'By Melanie', 'By Kaiting'}
        payer = check_label(payer_labels, record['Categories'])
        if payer == 'By Melanie': cc = 'MELA'
        else: cc = 'KMAN'

    owner_map = { 'For Both of Us': None,
      'For Melanie': 'Melanie Plageman',
      'For Kaiting': 'Kaiting Chen' }
    owner = owner_map[check_label(set(owner_map.keys()), record['Categories'])]

    return Transaction(
        merchant_name = record['Store'],
        cc = cc,
        amount = Decimal(record['Total (USD)']),
        # remote_id is the last path component of Link
        remote_id = record['Link'].split('/')[-1],
        owner = owner,
        transaction_date = transaction_date
    )
