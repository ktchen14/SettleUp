import itertools
import unicodecsv
import re
import collections
from datetime import datetime
from decimal import Decimal

# create named tuple which is all of the target fields
Transaction = collections.namedtuple('Transaction', [
    'amount', 'merchant_name', 'cc', 'owner', 'remote_id', 'transaction_date'
])

# compile regex for credit card
card = re.compile(r'Card \(([0-9]{4})\)')

class ShoeboxedCSVReader(object):
    prefix_mark = {
        'Date', 'Store', 'Total (USD)', 'Payment Type', 'Categories', 'Link'
    }

    # assume that the transaction section header is a record having at least:
    #   Date, Store, Total (USD), Payment Type, Categories, Link
    # if there is no such record then the export format has changed
    # and we don't have the requisite fields to proceed
    @staticmethod
    def is_transaction_prefix(record):
        return set(record).issuperset(ShoeboxedCSVReader.prefix_mark)

    # the transaction section is followed by a blank record
    @staticmethod
    def is_transaction_suffix(record):
        return len([f for f in record if f]) == 0

    def __init__(self, f):
        isnt_transaction_prefix = lambda x: not self.is_transaction_prefix(x)
        isnt_transaction_suffix = lambda x: not self.is_transaction_suffix(x)

        self.reader = itertools.takewhile(isnt_transaction_suffix,
                      itertools.dropwhile(isnt_transaction_prefix,
                      unicodecsv.reader(f)))

        # we want to fail here if no records match is_transaction_prefix
        self.header = next(self.reader)

    def __iter__(self):
        return self

    def next(self):
        for record in self.reader:
            record = dict(zip(self.header, record))
            record['Categories'] = record['Categories'].split(', ')
            if 'NYC' not in record['Categories']:
                return ShoeboxedCSVReader.record_to_transaction(record)
        raise StopIteration

    @staticmethod
    def check_label(labels, labelslist):
        categories = set(labelslist)
        intersection = categories.intersection(labels)
        if len(intersection) == 1: return tuple(intersection)[0]
        else: raise ValueError('Incorrect labels')

    @staticmethod
    def check_required_fields(record):
        for field in ['Total (USD)', 'Link', 'Date', 'Store']:
            if not record[field]: raise ValueError('Missing required value')

    @staticmethod
    def cs_date(record):
        return datetime.strptime(record['Date'], '%b %d, %Y').date()

    @staticmethod
    def set_payer(record):
        result = card.match(record['Payment Type'])
        if result:
            return result.group(1)
        else:
            payer_labels = {'By Melanie', 'By Kaiting'}
            payer = ShoeboxedCSVReader.check_label(payer_labels, record['Categories'])
            if payer == 'By Melanie': return 'MELA'
            else: return 'KMAN'

    @staticmethod
    def set_owner(record):
        owner_map = { 'For Both of Us': None,
          'For Melanie': 'Melanie Plageman',
          'For Kaiting': 'Kaiting Chen' }
        owner = owner_map[ShoeboxedCSVReader.check_label(set(owner_map.keys()), record['Categories'])]
        return owner

    @staticmethod
    def record_to_transaction(record):
        ShoeboxedCSVReader.check_required_fields(record)
        return Transaction(
            merchant_name = record['Store'],
            cc = ShoeboxedCSVReader.set_payer(record),
            amount = Decimal(record['Total (USD)']),
            # remote_id is the last path component of Link
            remote_id = record['Link'].split('/')[-1],
            owner = ShoeboxedCSVReader.set_owner(record),
            transaction_date = ShoeboxedCSVReader.cs_date(record)
        )
