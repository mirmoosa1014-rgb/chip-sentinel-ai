import unittest
from chipsentinel.engine import RegisterBank


class RegisterIndices(unittest.TestCase):
    def test_invalid_indices_reject_atomically(self):
        for writes in ({True:0},{0:True},{1.0:0},{0:1.0},{'1':0},{0:None},{0:1,2:4}):
            bank=RegisterBank();bank.values=[1,2,3,4]
            with self.subTest(writes=writes),self.assertRaises(ValueError):bank.edge(writes)
            self.assertEqual(bank.values,[1,2,3,4])
