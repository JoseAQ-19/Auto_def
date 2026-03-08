import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from phase3_assembly import Phase3Assembly

class TestPhase3Assembly(unittest.TestCase):
    def setUp(self):
        self.assembly = Phase3Assembly()
        self.test_plan_path = self.assembly.plan_path
        self.test_output = self.assembly.final_output
        self.fake_video = os.path.join(os.path.dirname(self.test_plan_path), "fake_video.mp4")
        
        # Simular un JSON correcto tras Fases 1 y 2
        mock_plan = [
            {"type": "podcast", "video_file": self.fake_video},
            {"type": "action", "video_file": self.fake_video}
        ]
        
        with open(self.test_plan_path, "w", encoding="utf-8") as f:
            json.dump(mock_plan, f)
            
        with open(self.fake_video, "w") as f:
            f.write("mock_video_bytes")

    def tearDown(self):
        if os.path.exists(self.test_plan_path):
            os.remove(self.test_plan_path)
        if os.path.exists(self.fake_video):
            os.remove(self.fake_video)
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    @patch("shutil.copy")
    def test_assembly_moviepy_success(self, mock_copy):
        import sys
        mock_moviepy = MagicMock()
        mock_moviepy_editor = MagicMock()
        sys.modules["moviepy"] = mock_moviepy
        sys.modules["moviepy.editor"] = mock_moviepy_editor
        
        mock_final_clip = MagicMock()
        mock_moviepy_editor.concatenate_videoclips.return_value = mock_final_clip
        
        result = self.assembly.execute()
        
        self.assertTrue(result)
        mock_moviepy_editor.concatenate_videoclips.assert_called_once()
        mock_final_clip.write_videofile.assert_called_once_with(self.test_output, fps=24, logger=None)

    @patch("shutil.copy")
    def test_assembly_single_file_fallback(self, mock_copy):
        # Rompemos el JSON para que solo haya 1 video
        with open(self.test_plan_path, "w", encoding="utf-8") as f:
            json.dump([{"type": "podcast", "video_file": self.fake_video}], f)
            
        result = self.assembly.execute()
        
        self.assertTrue(result)
        mock_copy.assert_called_once_with(self.fake_video, self.test_output)

if __name__ == "__main__":
    unittest.main()
