"""Unit tests for AI modules — LLMClient, DesignAgent, SmartChat, AIDesignGenerator, AISimulator."""

from __future__ import annotations

import unittest
from unittest.mock import patch
from typing import Any, Dict

from eostudio.core.ai.llm_client import LLMClient, LLMConfig
from eostudio.core.ai.agent import DesignAgent
from eostudio.core.ai.smart_chat import SmartChat, EditorContext, ChatResponse
from eostudio.core.ai.generator import AIDesignGenerator
from eostudio.core.ai.simulator import AISimulator


class MockLLMClient(LLMClient):
    """LLM client that returns canned responses without network calls."""

    def __init__(self, response: str = "Mock response") -> None:
        super().__init__(LLMConfig())
        self._response = response

    def chat(self, messages: list) -> str:
        return self._response

    def chat_json(self, messages: list) -> Dict[str, Any]:
        import json
        try:
            return json.loads(self._response)
        except json.JSONDecodeError:
            return {"error": "parse error", "raw": self._response}

    def is_available(self) -> bool:
        return True


class TestLLMConfig(unittest.TestCase):
    def test_default_ollama_endpoint(self) -> None:
        config = LLMConfig(provider="ollama")
        self.assertEqual(config.endpoint, "http://localhost:11434")

    def test_default_openai_endpoint(self) -> None:
        config = LLMConfig(provider="openai")
        self.assertEqual(config.endpoint, "https://api.openai.com")

    def test_custom_endpoint(self) -> None:
        config = LLMConfig(provider="ollama", endpoint="http://custom:1234")
        self.assertEqual(config.endpoint, "http://custom:1234")

    def test_effective_endpoint_strips_slash(self) -> None:
        config = LLMConfig(endpoint="http://example.com/")
        self.assertEqual(config.effective_endpoint(), "http://example.com")

    def test_default_values(self) -> None:
        config = LLMConfig()
        self.assertEqual(config.model, "llama3")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 2048)


class TestLLMClient(unittest.TestCase):
    def test_from_env_defaults(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            client = LLMClient.from_env()
            self.assertEqual(client.config.provider, "ollama")
            self.assertEqual(client.config.model, "llama3")

    def test_from_env_openai(self) -> None:
        env = {
            "EOSTUDIO_LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "EOSTUDIO_LLM_MODEL": "gpt-4o",
        }
        with patch.dict("os.environ", env, clear=True):
            client = LLMClient.from_env()
            self.assertEqual(client.config.provider, "openai")
            self.assertEqual(client.config.api_key, "sk-test")
            self.assertEqual(client.config.model, "gpt-4o")

    def test_prepend_system(self) -> None:
        config = LLMConfig(system_prompt="Be helpful")
        client = LLMClient(config)
        messages = [{"role": "user", "content": "hello"}]
        result = client._prepend_system(messages)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "system")
        self.assertEqual(result[0]["content"], "Be helpful")

    def test_no_duplicate_system(self) -> None:
        config = LLMConfig(system_prompt="Be helpful")
        client = LLMClient(config)
        messages = [
            {"role": "system", "content": "Existing"},
            {"role": "user", "content": "hello"},
        ]
        result = client._prepend_system(messages)
        self.assertEqual(len(result), 2)

    def test_unavailable_message(self) -> None:
        msg = LLMClient._unavailable_message("test error")
        self.assertIn("LLM backend is not available", msg)
        self.assertIn("test error", msg)


class TestDesignAgent(unittest.TestCase):
    def test_ask_returns_response(self) -> None:
        agent = DesignAgent()
        agent._client = MockLLMClient("Test answer")
        result = agent.ask("What is a cube?")
        self.assertEqual(result, "Test answer")

    def test_ask_maintains_history(self) -> None:
        agent = DesignAgent()
        agent._client = MockLLMClient("Answer 1")
        agent.ask("Question 1")
        self.assertEqual(len(agent._history), 2)

    def test_suggest_improvements_parses_list(self) -> None:
        agent = DesignAgent()
        agent._client = MockLLMClient('["Improve A", "Improve B"]')
        result = agent.suggest_improvements({"components": []})
        self.assertEqual(len(result), 2)
        self.assertIn("Improve A", result)

    def test_suggest_improvements_handles_error(self) -> None:
        agent = DesignAgent()
        agent._client = MockLLMClient("not json")
        result = agent.suggest_improvements({"components": []})
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_set_domain(self) -> None:
        agent = DesignAgent(domain="general")
        agent.set_domain("cad")
        self.assertEqual(agent.domain, "cad")
        self.assertIn("CAD", agent.client.config.system_prompt)

    def test_clear_history(self) -> None:
        agent = DesignAgent()
        agent._client = MockLLMClient("response")
        agent.ask("question")
        agent.clear_history()
        self.assertEqual(len(agent._history), 0)

    def test_generate_design_brief(self) -> None:
        response = '{"name": "Login Page", "type": "ui", "components": [], "layout": "vertical"}'
        agent = DesignAgent()
        agent._client = MockLLMClient(response)
        result = agent.generate_design_brief("A login page")
        self.assertEqual(result["name"], "Login Page")


class TestSmartChat(unittest.TestCase):
    def test_creation_with_editor_type(self) -> None:
        chat = SmartChat(editor_type="cad")
        self.assertEqual(chat.editor_type, "cad")
        self.assertIn("CAD", chat.client.config.system_prompt)

    def test_send_message(self) -> None:
        client = MockLLMClient("Design advice")
        chat = SmartChat(editor_type="ui", llm_client=client)
        response = chat.send_message("Help me with layout")
        self.assertIsInstance(response, ChatResponse)
        self.assertEqual(response.content, "Design advice")

    def test_send_message_with_context(self) -> None:
        client = MockLLMClient("Context-aware response")
        chat = SmartChat(editor_type="ui", llm_client=client)
        context = EditorContext(
            editor_type="ui",
            current_design={"components": [{"type": "Button"}]},
        )
        response = chat.send_message("What should I add?", context)
        self.assertTrue(response.context_used)

    def test_sample_prompts(self) -> None:
        chat = SmartChat(editor_type="cad")
        prompts = chat.get_sample_prompts()
        self.assertIsInstance(prompts, list)
        self.assertGreater(len(prompts), 0)

    def test_sample_prompts_default(self) -> None:
        chat = SmartChat(editor_type="unknown_editor")
        prompts = chat.get_sample_prompts()
        self.assertGreater(len(prompts), 0)

    def test_history_management(self) -> None:
        client = MockLLMClient("reply")
        chat = SmartChat(llm_client=client)
        chat.send_message("hello")
        self.assertEqual(chat.message_count, 2)
        chat.clear_history()
        self.assertEqual(chat.message_count, 0)

    def test_editor_context_summarize(self) -> None:
        ctx = EditorContext(
            editor_type="cad", project_name="Bracket",
            selected_components=[{"type": "cube"}],
        )
        summary = ctx.summarize()
        self.assertIn("Bracket", summary)
        self.assertIn("cad", summary)
        self.assertIn("cube", summary)


class TestAIDesignGenerator(unittest.TestCase):
    def test_text_to_ui(self) -> None:
        response = '{"name": "Login", "components": [{"type": "Input", "label": "Email"}], "layout": "vertical"}'
        client = MockLLMClient(response)
        gen = AIDesignGenerator(llm_client=client)
        result = gen.text_to_ui("A login form")
        self.assertEqual(result["name"], "Login")
        self.assertEqual(len(result["components"]), 1)

    def test_text_to_ui_fallback(self) -> None:
        client = MockLLMClient("not json at all")
        gen = AIDesignGenerator(llm_client=client)
        result = gen.text_to_ui("A login form")
        self.assertIn("components", result)
        self.assertEqual(result["metadata"]["source"], "fallback")

    def test_text_to_3d(self) -> None:
        response = '{"name": "Scene", "objects": [{"type": "cube", "position": [0,0,0]}]}'
        client = MockLLMClient(response)
        gen = AIDesignGenerator(llm_client=client)
        result = gen.text_to_3d("A simple cube")
        self.assertIn("objects", result)
        self.assertIn("lights", result)
        self.assertIn("camera", result)

    def test_text_to_cad(self) -> None:
        response = '{"name": "Bracket", "features": [{"type": "cube"}], "parameters": {"width": 50}}'
        client = MockLLMClient(response)
        gen = AIDesignGenerator(llm_client=client)
        result = gen.text_to_cad("An L-bracket")
        self.assertEqual(result["name"], "Bracket")
        self.assertEqual(result["units"], "mm")

    def test_refine_design(self) -> None:
        response = '{"name": "Updated", "components": [{"type": "Button", "label": "Submit"}]}'
        client = MockLLMClient(response)
        gen = AIDesignGenerator(llm_client=client)
        original = {"name": "Original", "components": []}
        result = gen.refine_design(original, "Add a submit button")
        self.assertEqual(result["name"], "Updated")


class TestAISimulator(unittest.TestCase):
    def test_detect_instability_nan(self) -> None:
        sim = AISimulator(llm_client=MockLLMClient(""))
        signals = {"output": [1.0, 2.0, float("nan"), 4.0]}
        warnings = sim.detect_instability(signals)
        self.assertGreater(len(warnings), 0)
        self.assertIn("NaN", warnings[0])

    def test_detect_instability_inf(self) -> None:
        sim = AISimulator(llm_client=MockLLMClient(""))
        signals = {"output": [1.0, float("inf")]}
        warnings = sim.detect_instability(signals)
        self.assertGreater(len(warnings), 0)

    def test_detect_instability_extreme_values(self) -> None:
        sim = AISimulator(llm_client=MockLLMClient(""))
        signals = {"output": [1e7] * 20}
        warnings = sim.detect_instability(signals)
        self.assertGreater(len(warnings), 0)
        self.assertIn("extreme", warnings[0])

    def test_detect_instability_stable(self) -> None:
        sim = AISimulator(llm_client=MockLLMClient(""))
        signals = {"output": [1.0] * 30}
        warnings = sim.detect_instability(signals)
        self.assertEqual(len(warnings), 0)

    def test_detect_instability_growing(self) -> None:
        sim = AISimulator(llm_client=MockLLMClient(""))
        values = [float(i ** 2) for i in range(20)]
        signals = {"output": values}
        warnings = sim.detect_instability(signals)
        self.assertGreater(len(warnings), 0)

    def test_default_parameters(self) -> None:
        result = AISimulator._default_parameters({"blocks": [1, 2, 3]})
        self.assertIn("dt", result)
        self.assertIn("duration", result)
        self.assertEqual(result["dt"], 0.01)

    def test_recommend_controller_fallback(self) -> None:
        client = MockLLMClient("not json")
        sim = AISimulator(llm_client=client)
        result = sim.recommend_controller("A DC motor")
        self.assertEqual(result["controller_type"], "PID")
        self.assertIn("Kp", result["gains"])

    def test_suggest_parameters(self) -> None:
        response = '{"dt": 0.005, "duration": 15.0, "block_parameters": {}, "reasoning": "Fine step"}'
        client = MockLLMClient(response)
        sim = AISimulator(llm_client=client)
        result = sim.suggest_parameters({"blocks": []})
        self.assertEqual(result["dt"], 0.005)


if __name__ == "__main__":
    unittest.main()
