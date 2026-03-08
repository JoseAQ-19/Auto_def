import os
import sys
import unittest
import json

# Modify path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from phase1_brain import Phase1Brain

class TestPhase1Brain(unittest.TestCase):
    def setUp(self):
        os.environ["ELEVENLABS_API_KEY"] = "mock_key_for_test"
        self.brain = Phase1Brain()

    def test_llm_json_generation(self):
        # We test the direct generation of LLM Script without audio payload
        test_prompt = "Escribe un artículo corto sobre IA generativa"
        result = self.brain.get_llm_script(test_prompt)
        
        self.assertIsInstance(result, list, "El resultado no es una lista")
        self.assertGreater(len(result), 0, "La lista está vacía")
        
        for item in result:
            self.assertIn("type", item, "Falta etiqueta 'type'")
            self.assertIn(item["type"], ["podcast", "action"], "El tipo debe ser podcast o action")
            
            if item["type"] == "podcast":
                self.assertIn("text", item, "Falta texto en tipo podcast")
            elif item["type"] == "action":
                self.assertIn("prompt", item, "Falta prompt en tipo action")

if __name__ == '__main__':
    unittest.main()
