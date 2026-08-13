"""LLM clients — Anthropic or OpenAI via plain HTTP (no SDK dependency)."""

from __future__ import annotations

import json

import httpx

from .. import config


class LLMUnavailable(RuntimeError):
    pass


def _pick_client():
    """Create the LLM client the env vars allow; raise LLMUnavailable if none."""
    if config.ANTHROPIC_API_KEY:
        return AnthropicClient(config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL)
    if config.OPENAI_API_KEY:
        return OpenAIClient(config.OPENAI_API_KEY, config.OPENAI_MODEL)
    raise LLMUnavailable("no API key configured (ANTHROPIC_API_KEY / OPENAI_API_KEY)")


class AnthropicClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def complete(self, system: str, user: str, max_tokens: int = 600) -> str:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=config.LLM_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(
            b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
        )

    def explain(self, evidence: dict) -> str:
        from . import base

        payload = json.dumps(evidence, indent=2, ensure_ascii=False)
        return self.complete(
            base.SYSTEM_PROMPT,
            f"Write an investigator-facing explanation of this flag.\n\nEVIDENCE (JSON):\n{payload}",
        )

    def translate_query(self, question: str, context: dict) -> str:
        from ..agent import translate

        payload = json.dumps(context, ensure_ascii=False)
        return self.complete(
            translate.SYSTEM_PROMPT,
            f"QUESTION: {question}\n\nAVAILABLE CONTEXT (entities, tools, syntax):\n{payload}\n\n"
            "Return ONLY the JSON plan.",
            max_tokens=500,
        )


class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _chat(self, system: str, user: str, max_tokens: int = 600) -> str:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=config.LLM_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def explain(self, evidence: dict) -> str:
        from . import base

        payload = json.dumps(evidence, indent=2, ensure_ascii=False)
        return self._chat(
            base.SYSTEM_PROMPT,
            f"Write an investigator-facing explanation of this flag.\n\nEVIDENCE (JSON):\n{payload}",
        )

    def translate_query(self, question: str, context: dict) -> str:
        from ..agent import translate

        payload = json.dumps(context, ensure_ascii=False)
        return self._chat(
            translate.SYSTEM_PROMPT,
            f"QUESTION: {question}\n\nAVAILABLE CONTEXT (entities, tools, syntax):\n{payload}\n\n"
            "Return ONLY the JSON plan.",
            max_tokens=500,
        )

