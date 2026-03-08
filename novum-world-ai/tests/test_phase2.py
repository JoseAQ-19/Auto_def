import os
import sys
import unittest
import json
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from phase2_sets import Phase2Sets

class TestPhase2Sets(unittest.TestCase):
    def setUp(self):
        # Asegurarse de que las credenciales no fallen en mock
        os.environ["HF_SPACE_PODCAST_URL"] = "https://mock.podcast.space"
        os.environ["HF_SPACE_ACTION_URL"] = "https://mock.action.space"
        os.environ["HF_TOKEN_PODCAST"] = "mock_token"
        os.environ["HF_TOKEN_ACTION"] = "mock_token"
        
        self.sets = Phase2Sets()
        self.test_plan_path = self.sets.plan_path
        
        # Simular JSON que saldría de la Fase 1
        mock_plan = [
            {"type": "podcast", "audio_file": "mock_audio.wav"},
            {"type": "action", "prompt": "Ciberataque"}
        ]
        
        with open(self.test_plan_path, "w", encoding="utf-8") as f:
            json.dump(mock_plan, f)
            
        with open("mock_audio.wav", "wb") as f:
            f.write(b"mock_audio")

    def tearDown(self):
        # Limpieza de mocks generados
        if os.path.exists(self.test_plan_path):
            os.remove(self.test_plan_path)
        if os.path.exists("mock_audio.wav"):
            os.remove("mock_audio.wav")

    @patch("video_engine.VideoEngine.generate_podcast_video")
    @patch("video_engine.VideoEngine.generate_action_video")
    def test_set_processing_success(self, mock_action, mock_podcast):
        mock_podcast.return_value = "scene_0.mp4"
        mock_action.return_value = "scene_1.mp4"
        
        result = self.sets.execute()
        
        self.assertTrue(result)
        self.assertEqual(mock_podcast.call_count, 1)
        self.assertEqual(mock_action.call_count, 1)
        
        # Validar nuevo shooting_plan guardado se actualizó con paths
        with open(self.test_plan_path, "r") as f:
            updated_plan = json.load(f)
            self.assertEqual(updated_plan[0].get("video_file"), "scene_0.mp4")
            self.assertEqual(updated_plan[1].get("video_file"), "scene_1.mp4")

    @patch("video_engine.VideoEngine.generate_podcast_video")
    @patch("phase2_sets.Phase2Sets.audit_and_fix_space")
    def test_audit_trigger_on_500(self, mock_audit, mock_podcast):
        # Probar la autocorrección. Si predict() crashea simulando error 500,
        # debe activarse audit_and_fix_space para reiniciar HF.
        mock_podcast.side_effect = Exception("HTTP 500 Server Error from HF Space")
        
        self.sets.execute()
        
        # El módulo de corrección debe enviar el reinicio / fix al Space implicado
        mock_audit.assert_called_once_with(self.sets.podcast_repo_id, self.sets.video_engine.podcast_token)
        
if __name__ == "__main__":
    unittest.main()
