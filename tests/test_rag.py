"""
Unit tests for RAGChatSession lifecycle and client reuse.
"""

import unittest
from unittest.mock import MagicMock, patch
from sr6core.rag.llm import RAGChatSession


class TestRAGChatSession(unittest.TestCase):
    @patch("sr6core.rag.llm.load_environment")
    @patch("os.getenv")
    def test_client_reused_across_multiple_queries(self, mock_getenv, mock_load_env):
        mock_getenv.return_value = "fake_api_key"

        mock_genai_module = MagicMock()
        mock_client_instance = MagicMock()
        mock_chat_instance = MagicMock()

        mock_genai_module.Client.return_value = mock_client_instance
        mock_client_instance.chats.create.return_value = mock_chat_instance

        mock_response = MagicMock()
        mock_response.text = "Answer from Gemini"
        mock_chat_instance.send_message.return_value = mock_response

        with patch.dict("sys.modules", {"google.genai": mock_genai_module, "google.genai.types": MagicMock()}):
            session = RAGChatSession(model_name="flash-latest")

            # First query
            text1, err1 = session.send_query("What is fading?", "Context 1")
            self.assertIsNone(err1)
            self.assertEqual(text1, "Answer from Gemini")

            # Second query
            text2, err2 = session.send_query("How to dodge?", "Context 2")
            self.assertIsNone(err2)
            self.assertEqual(text2, "Answer from Gemini")

            # genai.Client should only be called ONCE across both queries
            self.assertEqual(mock_genai_module.Client.call_count, 1)
            # chats.create should only be called ONCE
            self.assertEqual(mock_client_instance.chats.create.call_count, 1)
            # send_message should be called TWICE on the same chat object
            self.assertEqual(mock_chat_instance.send_message.call_count, 2)


if __name__ == "__main__":
    unittest.main()
