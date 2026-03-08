import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))

try:
    from video_engine import VideoEngine
except ImportError:
    from src.video_engine import VideoEngine

class TestVideoEngine(unittest.TestCase):
    def setUp(self):
        # Configuramos un entorno falso para no dar errores
        os.environ['HF_SPACE_PODCAST_URL'] = "http://podcast.space"
        os.environ['HF_SPACE_ACTION_URL'] = "http://action.space"
        os.environ['HF_TOKEN_PODCAST'] = "token1"
        os.environ['HF_TOKEN_ACTION'] = "token2"
        self.engine = VideoEngine()

    def test_init_missing_credentials(self):
        with patch.dict(os.environ, clear=True):
            engine = VideoEngine()
            # Debería crearse igual pero faltarán las flags, lo que lanzará error luego
            self.assertIsNone(engine.podcast_url)

    @patch('video_engine.os.rename')
    @patch('video_engine.Client')
    def test_generate_podcast_video_success(self, mock_client_class, mock_rename):
        mock_client = MagicMock()
        mock_client.predict.return_value = "/tmp/dummy_video.mp4"
        mock_client_class.return_value = mock_client

        with patch('video_engine.handle_file', return_value="handled_file"):
            output = self.engine.generate_podcast_video("dummy_audio.mp3", "master.png", "out.mp4")

            mock_client_class.assert_called_with("http://podcast.space", hf_token="token1")
            mock_client.predict.assert_called_once()
            mock_rename.assert_called_once_with("/tmp/dummy_video.mp4", "out.mp4")
            self.assertEqual(output, "out.mp4")

    @patch('video_engine.os.rename')
    @patch('video_engine.Client')
    def test_generate_action_video_success(self, mock_client_class, mock_rename):
        mock_client = MagicMock()
        mock_client.predict.return_value = "/tmp/dummy_action.mp4"
        mock_client_class.return_value = mock_client

        with patch('video_engine.handle_file', return_value="handled_file"):
            output = self.engine.generate_action_video("Walking scene", "master.png", "out_action.mp4")

            mock_client_class.assert_called_with("http://action.space", hf_token="token2")
            mock_client.predict.assert_called_once()
            mock_rename.assert_called_once_with("/tmp/dummy_action.mp4", "out_action.mp4")
            self.assertEqual(output, "out_action.mp4")

if __name__ == '__main__':
    unittest.main()
