import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), 'src')))

from main import NovumDirector

class TestNovumDirector(unittest.TestCase):
    def setUp(self):
        # Mocks para saltarse el init que comprueba claves
        with patch('main.AudioEngine'):
            with patch('main.VideoEngine'):
                self.director = NovumDirector()
        
        # Mocks para los motores
        self.director.audio_engine = MagicMock()
        self.director.video_engine = MagicMock()

    def test_process_scene_dialogue(self):
        scene = {"type": "dialogue", "text": "Test"}
        self.director.audio_engine.generate_audio.return_value = "scene_0.mp3"
        self.director.video_engine.generate_podcast_video.return_value = "scene_0.mp4"

        result = self.director.process_scene(scene, "master.png", 0)

        self.director.audio_engine.generate_audio.assert_called_once_with("Test", output_path="scene_0.mp3")
        self.director.video_engine.generate_podcast_video.assert_called_once_with(
            audio_path="scene_0.mp3",
            master_image_path="master.png",
            output_path="scene_0.mp4"
        )
        self.assertEqual(result, "scene_0.mp4")

    def test_process_scene_action(self):
        scene = {"type": "action", "prompt": "Walk"}
        self.director.video_engine.generate_action_video.return_value = "scene_1.mp4"

        result = self.director.process_scene(scene, "master.png", 1)

        self.director.video_engine.generate_action_video.assert_called_once_with(
            text_prompt="Walk",
            master_image_path="master.png",
            output_path="scene_1.mp4"
        )
        self.assertEqual(result, "scene_1.mp4")

    @patch('main.NovumDirector.assemble_videos')
    @patch('main.NovumDirector.process_scene')
    def test_run_daily_workflow_success(self, mock_process, mock_assemble):
        # Mocks de flujo de trabajo
        mock_process.side_effect = ["clip1.mp4", "clip2.mp4", "clip3.mp4"]
        mock_assemble.return_value = "final_test.mp4"

        # Simular script de 3 escenas
        with patch.object(self.director, 'get_todays_script', return_value=[{}, {}, {}]):
            result = self.director.run_daily_workflow("master.png")

        self.assertEqual(mock_process.call_count, 3)
        mock_assemble.assert_called_once_with(["clip1.mp4", "clip2.mp4", "clip3.mp4"])
        self.assertEqual(result, "final_test.mp4")

if __name__ == '__main__':
    unittest.main()
