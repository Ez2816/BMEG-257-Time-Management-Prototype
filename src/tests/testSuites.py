import unittest

from timeParser import parseFileToDictionary

#TODO: Implement test suites for DHF 5
# copilot set up general test suite structure for category parsing, time tracking, and priority verification

filePath1 = "src\\tests\\file1.txt"
filePath2 = "src\\tests\\file2.txt"
filePath3 = "src\\tests\\file3.txt"
# TODO: insert the hypothetical list of user priorities as an array

class TestCategoryParsing(unittest.TestCase):
    #Test suite for parsing time management categories
    
    def test_parse1(self):
        testDictionary = parseFileToDictionary(filePath1)
        self.assertEqual(testDictionary, {'Work': 240, 'Exercise': 60, 'Leisure': 120})
    
    def test_parse2(self):
        testDictionary = parseFileToDictionary(filePath2)
        self.assertEqual(len(testDictionary.keys()), 7)
        
    
    def test_parse3(self):
        testDictionary = parseFileToDictionary(filePath3)
        self.assertEqual(len(testDictionary.keys()), 0)
        




class TestPriorityVerification(unittest.TestCase):
    """Test suite for priority verification"""
    
    def test_priority_order_followed(self):
        """Test if priorities were followed in correct order"""
        pass
    
    def test_priority_time_allocation(self):
        """Test if sufficient time allocated to high priority tasks"""
        pass
    
    def test_priority_violations(self):
        """Test detection of priority violations"""
        pass


if __name__ == '__main__':
    unittest.main()