from __future__ import annotations

import json
from typing import Literal, List, Dict, Any, Callable

from openai import OpenAI
from openai.types import ChatModel
from openai.types.chat import ChatCompletionMessageParam


class Conversation:
    def __init__(self, openai_api_key: str, model: ChatModel = "gpt-4o-mini",
                 response_format: Literal["text", "json_object"] = "json_object"):
        self.messages: List[ChatCompletionMessageParam] = []
        self.response_format = response_format
        self.model = model
        self.openai_api_key = openai_api_key

        self.processor:Dict[Literal["text", "json_object"], Callable[[str], Any]] = {
            'text': lambda x:x,
            'json_object': json.loads
        }

    def as_system(self, system_prompt: str) -> Conversation:
        self.messages.append({
            "role": "system",
            "content": system_prompt,
        })
        return self

    def as_user(self, user_prompt: str) -> Conversation:
        self.messages.append({
            "role": "user",
            "content": user_prompt,
        })
        return self

    def complete(self):
        client = OpenAI(api_key=self.openai_api_key)
        chat_completion = client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            response_format={"type": self.response_format},
        )
        return self.processor[self.response_format](chat_completion.choices[0].message.content)
