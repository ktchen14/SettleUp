import itertools
import unicodecsv

# assume that the transaction section header is a record having at least:
#   Date, Store, Total (USD), Payment Type, Categories, Link
# if there is no such record then the export format has changed
# and we don't have the requisite fields to proceed
def is_transaction_prefix(record):
    mark = {'Date', 'Store', 'Total (USD)', 'Payment Type', 'Categories', 'Link'}
    return set(record).issuperset(mark)

# the transaction section is followed by a blank record
def is_transaction_suffix(record):
    return len([f for f in record if f]) == 0

class ShoeboxedCSVReader(object):
    def __init__(self, f):
        self.reader = itertools.takewhile(lambda x: not is_transaction_suffix(x),
                      itertools.dropwhile(lambda x: not is_transaction_prefix(x),
                      unicodecsv.reader(f)))

        # we want to fail here if no records match is_transaction_prefix
        self.header = self.reader.next()

    def __iter__(self): return iter(self.reader)

