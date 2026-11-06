import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from chipsentinel import model
from chipsentinel.engine import alu


class RankerValidation(unittest.TestCase):
    def test_corrupt_ranker_uses_unranked_fallback(self):
        original = json.loads(model.MODEL.read_text())
        invalid = ['{', 'null', json.dumps({**original, 'weights': [1]}),
                   json.dumps({**original, 'weights': [float('nan')] * 7}),
                   json.dumps({**original, 'schema': ['wrong']})]
        expected = [{'index': i, 'score': 0.0} for i in range(len(alu(6).hypotheses()))]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ranker.json'
            for content in invalid:
                with self.subTest(content=content):
                    path.write_text(content)
                    with patch.object(model, 'MODEL', path):
                        self.assertEqual(model.rank(6, []), expected)
