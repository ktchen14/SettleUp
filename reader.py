import itertools
import unicodecsv

class ShoeboxedCSVReader(object):
    # assume that the transaction section header is a record having at least:
    #   Date, Store, Total (USD), Payment Type, Categories, Link
    # if there is no such record then the export format has changed
    # and we don't have the requisite fields to proceed
    @staticmethod
    def is_transaction_prefix(record):
        prefix_mark = {
            'Date', 'Store', 'Total (USD)', 'Payment Type', 'Categories', 'Link'
        }
        return set(record).issuperset(prefix_mark)

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

    def __iter__(self): return iter(self.reader)

