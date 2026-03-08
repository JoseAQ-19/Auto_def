import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))

try:
    from audio_engine import AudioEngine
except ImportError:
    from src.audio_engine import AudioEngine

class TestAudioEngine(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key_123"
        self.engine = AudioEngine(api_key=self.api_key)

    def test_init_no_key(self):
        with patch.dict(os.environ, clear=True):
            with self.assertRaises(ValueError):
                AudioEngine()

    @patch('audio_engine.requests.post')
    def test_generate_audio_success(self, mock_post):
        # Mock de la respuesta de requests
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_post.return_value = mock_response

        # Mock del archivo a guardar
        m_open = mock_open()
        with patch('builtins.open', m_open):
            output_file = self.engine.generate_audio("Hola mundo", output_path="dummy.mp3")

        # Verificar llamadas
        mock_post.assert_called_once()
        self.assertEqual(output_file, "dummy.mp3")
        m_open.assert_called_once_with("dummy.mp3", "wb")
        m_open().write.assert_any_call(b"chunk1")
        m_open().write.assert_any_call(b"chunk2")

if __name__ == '__main__':
    unittest.main()
