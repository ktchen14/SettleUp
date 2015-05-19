import cs
import unittest

class TestCSFunctions(unittest.TestCase):
    
    def test_check_label(self):
        labels = {'His', 'Hers'}
        labelslist = ['His', 'Theirs']
        self.assertEqual(cs.check_label(labels, labelslist), 'His')

    def test_record_to_transaction(self):
        # row = { 'Payment Type':'Card (8349)', 'Store':'Whole Foods Market' }
        pass

if __name__ == '__main__':
    unittest.main()
