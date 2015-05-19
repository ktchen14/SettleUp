import reader
import unittest

class TestReaderFunctions(unittest.TestCase):
    
    def test_is_transaction_prefix(self):
        row = ['Date', 'Store', 'Total (USD)', 'Payment Type', 'Categories', 'Link', 'Description', 'Vendor']
        self.assertTrue(reader.ShoeboxedCSVReader.is_transaction_prefix(row))

    def test_is_transaction_suffix(self):
        row = ['', '', '', '', '']
        self.assertTrue(reader.ShoeboxedCSVReader.is_transaction_suffix(row))

if __name__ == '__main__':
    unittest.main()
