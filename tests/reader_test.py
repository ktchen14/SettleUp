from reader import ShoeboxedCSVReader, Transaction

import datetime
import decimal
import unittest

class TestReaderFunctions(unittest.TestCase):
    def setUp(self):
        self.test_record = {'Total (USD)': '14.26', 'Conversion Rate': '1.0000', 'Payment Type': 'Card (0000)', 'Original Total': '14.26', 'Original Currency': 'USD', 'Note': '', 'Link': 'https://app.shoeboxed.com/shared/view/abcdefgh-ijkl-mnop-qrst-uvwxyz012345', 'Categories': 'For Melanie', 'Date': 'Oct 01, 2014', 'Original Tax': '', 'Store': 'Harris Teeter', 'Tax (USD)': ''}
        self.single_file = 'tests/reader_test.csv'

    def test_is_transaction_prefix(self):
        # is_transaction_prefix should return False if any of the fields:
        #   Date, Store, Total (USD), Payment Type, Categories, Link
        # are missing
        record = ['Store', 'Date', 'Total (USD)', 'Link', 'Payment Type']
        self.assertFalse(ShoeboxedCSVReader.is_transaction_prefix(record))

        # should return True if all of the fields are present; extraneous
        # fields should not affect this
        record = ['Store', 'Date', 'Tax (USD)', 'Total (USD)', 'Link',
                'Conversion Rate', 'Categories', 'Payment Type']
        self.assertTrue(ShoeboxedCSVReader.is_transaction_prefix(record))

    def test_is_transaction_suffix(self):
        # is_transaction_suffix should return True if all elements of the
        # record are blank
        record = ['', '', '', '', '']
        self.assertTrue(ShoeboxedCSVReader.is_transaction_suffix(record))

        # whitespace in any field should result in returning False
        record = ['', ' ', '', ' ']
        self.assertFalse(ShoeboxedCSVReader.is_transaction_suffix(record))

    def test_cleanse_amount(self):
        # cleanse_amount should return "Total (USD)" as a decimal.Decimal
        self.test_record['Total (USD)'] = '14.26'
        result = ShoeboxedCSVReader.cleanse_amount(self.test_record)
        self.assertIsInstance(result, decimal.Decimal)

        # if "Total (USD)" is negative amount should be less than zero
        self.test_record['Total (USD)'] = '-12.34'
        result = ShoeboxedCSVReader.cleanse_amount(self.test_record)
        self.assertLess(result, 0)

        # if "Total (USD)" is all zeroes amount should evaluate to zero
        self.test_record['Total (USD)'] = '00.00'
        result = ShoeboxedCSVReader.cleanse_amount(self.test_record)
        self.assertEqual(result, 0)

    def test_cleanse_merchant_name(self):
        # cleanse_merchant_name should return "Store" as-is
        self.test_record['Store'] = 'Harris Teeter'
        result = ShoeboxedCSVReader.cleanse_merchant_name(self.test_record)
        self.assertEqual(result, 'Harris Teeter')

    def test_set_owner(self):
        # ensure that exactly one of these:
        #   For Both of Us, For Kaiting, For Melanie
        # is present in "Categories"
        self.test_record['Categories'] = ['For Kaiting', 'For Melanie']
        with self.assertRaises(Exception):
            ShoeboxedCSVReader.set_owner(self.test_record)

        self.test_record['Categories'] = []
        with self.assertRaises(Exception):
            ShoeboxedCSVReader.set_owner(self.test_record)

        # if 'For Both of Us' is present return None
        self.test_record['Categories'] = ['For Both of Us']
        result = ShoeboxedCSVReader.set_owner(self.test_record)
        self.assertIsNone(result)

        # if 'For Kaiting' is present return 'Kaiting Chen'
        self.test_record['Categories'] = ['For Kaiting']
        result = ShoeboxedCSVReader.set_owner(self.test_record)
        self.assertEqual(result, 'Kaiting Chen')

        # if 'For Melanie' is present return 'Melanie Plaeman'
        self.test_record['Categories'] = ['For Melanie']
        result = ShoeboxedCSVReader.set_owner(self.test_record)
        self.assertEqual(result, 'Melanie Plageman')

    def test_set_payer(self):
        # if "Payment Type" lists a card number then return that
        self.test_record['Payment Type'] = 'Card (0000)'
        result = ShoeboxedCSVReader.set_payer(self.test_record)
        self.assertEqual(result, '0000')

        # otherwise ensure that exactly one of these:
        #   By Kaiting, By Melanie
        # is present in "Categories"
        self.test_record['Payment Type'] = 'Card'

        self.test_record['Categories'] = ['By Kaiting', 'By Melanie']
        with self.assertRaises(Exception):
            ShoeboxedCSVReader.set_payer(self.test_record)

        self.test_record['Categories'] = []
        with self.assertRaises(Exception):
            ShoeboxedCSVReader.set_payer(self.test_record)

        # if 'By Kaiting' is present then return 'KMAN'
        # if 'By Melanie' is present then return 'MELA'
        self.test_record['Categories'] = ['By Kaiting']
        result = ShoeboxedCSVReader.set_payer(self.test_record)
        self.assertEqual(result, 'KMAN')

        self.test_record['Categories'] = ['By Melanie']
        result = ShoeboxedCSVReader.set_payer(self.test_record)
        self.assertEqual(result, 'MELA')

    def test_cleanse_remote_id(self):
        self.test_record['Link'] = '''
            https://app.shoeboxed.com/shared/view/abcdefgh-ijkl-mnop-qrst-uvwxyz012345'
        '''.strip()
        result = ShoeboxedCSVReader.cleanse_remote_id(self.test_record)
        self.assertRegexpMatches(result, '[a-z0-9]+(-[a-z0-9])*')

    def test_cs_date(self):
        # cleanse_transaction_date should return "Date" as a datetime.date
        self.test_record['Date'] = 'Oct 01, 2014'
        result = ShoeboxedCSVReader.cs_date(self.test_record)
        self.assertIsInstance(result, datetime.date)

        # if "Date" is invalid then raise an error
        self.test_record['Date'] = 'Oct 32, 2014'
        with self.assertRaises(Exception):
            ShoeboxedCSVReader.cs_date(self.test_record)

    def test_check_label(self):
        labels = {'His', 'Hers'}
        labelslist = ['His', 'Theirs']
        self.assertEqual(ShoeboxedCSVReader.check_label(labels, labelslist), 'His')

    def test_is_iterable(self):
        # the single_file is a CSV with a single transaction record
        with open(self.single_file, 'r') as csv_source:
            reader = ShoeboxedCSVReader(csv_source)

            # the reader object should be iterable
            for i, t in enumerate(reader):
                # each iteration should yield a Transaction
                self.assertIsInstance(t, Transaction)

        # the loop should have performed a single iteration
        self.assertEqual(i, 0)

if __name__ == '__main__':
    unittest.main()
