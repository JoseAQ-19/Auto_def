import unittest
from unittest.mock import patch, MagicMock
from src.telegram_notifier import send_telegram_message
from src.llm_agent import generate_novum_prompt
from src.gsc_client import get_top_performing_topic

class TestPhase1(unittest.TestCase):

    @patch('src.telegram_notifier.requests.post')
    @patch('src.telegram_notifier.os.getenv')
    def test_send_telegram_success(self, mock_getenv, mock_post):
        mock_getenv.side_effect = lambda k, d=None: "dummy_value" if k in ["TOKEN_TELEGRAM", "TELEGRAM_USER_ID"] else d
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        
        result = send_telegram_message("Test de notificación 🦑")
        self.assertTrue(result)
        mock_post.assert_called_once()
        
    @patch('src.llm_agent.OpenAI')
    @patch('src.llm_agent.os.getenv')
    def test_llm_agent_prompt(self, mock_getenv, mock_openai):
        mock_getenv.side_effect = lambda k, d=None: "fake_sk" if k == "HF_TOKEN_CEREBRO" else d
        
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "[Voz en Off]: Hola, soy Novum."
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        result = generate_novum_prompt("Prueba AI")
        self.assertEqual(result, "[Voz en Off]: Hola, soy Novum.")
        mock_openai.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()
