import reader
import unittest

class TestReaderFunctions(unittest.TestCase):
    def setUp(self):
        self.example_file = open('tests/reader_test.csv')
        self.example_reader = reader.ShoeboxedCSVReader(self.example_file)

    def tearDown(self):
        self.example_file.close()

    def test_is_transaction_prefix(self):
        row = ['Date', 'Store', 'Total (USD)', 'Payment Type', 'Categories', 'Link', 'Description', 'Vendor']
        self.assertTrue(reader.ShoeboxedCSVReader.is_transaction_prefix(row))

    # the test file has a single transaction record
    def test_is_iterable(self):
        # first iteration should work
        next(iter(self.example_reader))

        # second iteration should stop iteration
        with self.assertRaises(StopIteration):
            next(iter(self.example_reader))

if __name__ == '__main__':
    unittest.main()
