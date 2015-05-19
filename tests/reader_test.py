from reader import ShoeboxedCSVReader

import unittest

class TestReaderFunctions(unittest.TestCase):
    def setUp(self):
        self.example_file = open('tests/reader_test.csv')
        self.example_reader = ShoeboxedCSVReader(self.example_file)

    def tearDown(self):
        self.example_file.close()

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

    # the test file has a single transaction record
    def test_is_iterable(self):
        # first iteration should work
        next(iter(self.example_reader))

        # second iteration should stop iteration
        with self.assertRaises(StopIteration):
            next(iter(self.example_reader))

if __name__ == '__main__':
    unittest.main()
