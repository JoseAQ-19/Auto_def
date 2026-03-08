import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))

from data_scanner import DataScanner

class TestDataScanner(unittest.TestCase):
    def setUp(self):
        # Configurar un entorno falso
        os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = '{"type": "service_account"}'
        os.environ["GSC_SITE_URL"] = "sc-domain:test.com"
        self.scanner = DataScanner()

    def test_init_missing_credentials(self):
        with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS_JSON": ""}):
            scanner = DataScanner()
            self.assertIsNone(scanner.gcp_json)

    @patch('data_scanner.DataScanner._fetch_from_mcp')
    def test_get_top_article_success(self, mock_fetch):
        # Mock asíncrono
        future = asyncio.Future()
        future.set_result([{"keys": ["https://novum.world/test-ia"], "impressions": 1000}])
        mock_fetch.return_value = future

        result = self.scanner.get_top_article()
        self.assertEqual(result, "https://novum.world/test-ia")

    @patch('data_scanner.DataScanner._fetch_from_mcp')
    def test_get_top_article_fallback_empty(self, mock_fetch):
        future = asyncio.Future()
        future.set_result([])
        mock_fetch.return_value = future

        result = self.scanner.get_top_article()
        self.assertEqual(result, "https://novum.world/articulos/tendencias-ia-default")

    def test_compose_prompt_for_script(self):
        url = "https://novum.world/articulos/la-nueva-revolucion"
        prompt = self.scanner.compose_prompt_for_script(url)
        self.assertIn("la nueva revolucion", prompt)
        self.assertIn("60 segundos", prompt)

if __name__ == '__main__':
    unittest.main()
