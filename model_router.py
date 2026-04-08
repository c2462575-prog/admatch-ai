# -*- coding: utf-8 -*-
"""
Model Router - Central API routing with dynamic model selection and logging
"""

import os
import time
from typing import Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime

from google import genai
from google.genai import types


# Model configurations
MODELS = {
    "PRO": "gemini-3.1-pro-preview",
    "FLASH": "gemini-3-flash-preview",
    "FLASH_LITE": "gemini-3.1-flash-lite-preview",
    "EMBED": "gemini-embedding-2-preview"
}

ThinkingLevel = Literal["HIGH", "MEDIUM", "LOW"]


@dataclass
class APICallLog:
    """Log entry for an API call"""
    timestamp: str
    task: str
    model: str
    thinking_level: Optional[str]
    success: bool
    retry_count: int
    error_message: Optional[str] = None


@dataclass
class ModelRouterStats:
    """Statistics for model usage"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    calls_by_model: dict = field(default_factory=dict)
    calls_by_task: dict = field(default_factory=dict)
    logs: list = field(default_factory=list)


class ModelRouter:
    """Central router for all Gemini API calls with logging and retry logic"""

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)
        self.stats = ModelRouterStats()

    def _log_call(self, task: str, model: str, thinking_level: Optional[str],
                  success: bool, retry_count: int, error_message: Optional[str] = None):
        """Log an API call"""
        log_entry = APICallLog(
            timestamp=datetime.now().isoformat(),
            task=task,
            model=model,
            thinking_level=thinking_level,
            success=success,
            retry_count=retry_count,
            error_message=error_message
        )
        self.stats.logs.append(log_entry)
        self.stats.total_calls += 1

        if success:
            self.stats.successful_calls += 1
        else:
            self.stats.failed_calls += 1

        # Track by model
        if model not in self.stats.calls_by_model:
            self.stats.calls_by_model[model] = {"success": 0, "failed": 0}
        if success:
            self.stats.calls_by_model[model]["success"] += 1
        else:
            self.stats.calls_by_model[model]["failed"] += 1

        # Track by task
        if task not in self.stats.calls_by_task:
            self.stats.calls_by_task[task] = {"success": 0, "failed": 0}
        if success:
            self.stats.calls_by_task[task]["success"] += 1
        else:
            self.stats.calls_by_task[task]["failed"] += 1

        # Print log
        level_str = f"/{thinking_level}" if thinking_level else ""
        status = "SUCCESS" if success else f"FAILED ({error_message})"
        retry_str = f" (retry {retry_count})" if retry_count > 0 else ""
        print(f"[API] {task}: {model}{level_str} - {status}{retry_str}")

    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate backoff delay: 1s, 2s, 4s"""
        return 2 ** attempt

    def generate_content(
        self,
        task: str,
        prompt: str,
        model_key: str = "PRO",
        thinking_level: Optional[ThinkingLevel] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate content with specified model and thinking level

        Args:
            task: Description of the task (for logging)
            prompt: The prompt to send
            model_key: Key from MODELS dict (PRO, FLASH, FLASH_LITE)
            thinking_level: HIGH, MEDIUM, or LOW (None for no thinking)
            max_retries: Maximum retry attempts

        Returns:
            Generated text or None if failed
        """
        model = MODELS.get(model_key, MODELS["PRO"])

        # Build config
        config = {}
        if thinking_level:
            config["thinking_config"] = types.ThinkingConfig(thinking_level=thinking_level)

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config if config else None
                )

                # Extract text from response
                result_text = response.text if response.text else ""

                self._log_call(task, model, thinking_level, True, attempt)
                return result_text

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    print(f"[RETRY] {task}: Attempt {attempt + 1} failed, waiting {delay}s...")
                    time.sleep(delay)

        self._log_call(task, model, thinking_level, False, max_retries - 1, last_error)
        return None

    def generate_embedding(
        self,
        task: str,
        text: str,
        max_retries: int = 3
    ) -> Optional[list]:
        """
        Generate embedding vector for text

        Args:
            task: Description of the task (for logging)
            text: Text to embed
            max_retries: Maximum retry attempts

        Returns:
            Embedding vector or None if failed
        """
        model = MODELS["EMBED"]

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.embed_content(
                    model=model,
                    contents=text
                )

                # Extract embedding
                if response.embeddings and len(response.embeddings) > 0:
                    embedding = response.embeddings[0].values
                    self._log_call(task, model, None, True, attempt)
                    return embedding
                else:
                    raise ValueError("No embedding returned")

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    print(f"[RETRY] {task}: Attempt {attempt + 1} failed, waiting {delay}s...")
                    time.sleep(delay)

        self._log_call(task, model, None, False, max_retries - 1, last_error)
        return None

    def get_stats_summary(self) -> str:
        """Get a summary of API usage statistics"""
        lines = [
            "=" * 50,
            "API USAGE STATISTICS",
            "=" * 50,
            f"Total Calls: {self.stats.total_calls}",
            f"Successful: {self.stats.successful_calls}",
            f"Failed: {self.stats.failed_calls}",
            "",
            "Calls by Model:",
        ]

        for model, counts in self.stats.calls_by_model.items():
            lines.append(f"  {model}: {counts['success']} success, {counts['failed']} failed")

        lines.append("")
        lines.append("Calls by Task:")
        for task, counts in self.stats.calls_by_task.items():
            lines.append(f"  {task}: {counts['success']} success, {counts['failed']} failed")

        lines.append("=" * 50)
        return "\n".join(lines)

    def get_stats_dict(self) -> dict:
        """Get statistics as dictionary for report generation"""
        return {
            "total_calls": self.stats.total_calls,
            "successful_calls": self.stats.successful_calls,
            "failed_calls": self.stats.failed_calls,
            "calls_by_model": self.stats.calls_by_model,
            "calls_by_task": self.stats.calls_by_task,
            "logs": [
                {
                    "timestamp": log.timestamp,
                    "task": log.task,
                    "model": log.model,
                    "thinking_level": log.thinking_level,
                    "success": log.success
                }
                for log in self.stats.logs
            ]
        }


# Task-specific helper functions
def get_router() -> ModelRouter:
    """Get or create a ModelRouter instance"""
    return ModelRouter()


# Predefined task configurations
TASK_CONFIGS = {
    "agent_analysis": {"model_key": "PRO", "thinking_level": "HIGH"},
    "embedding_description": {"model_key": "FLASH", "thinking_level": "MEDIUM"},
    "negotiation_dialogue": {"model_key": "PRO", "thinking_level": "MEDIUM"},
    "audience_scoring": {"model_key": "FLASH_LITE", "thinking_level": "LOW"},
    "audience_intervention": {"model_key": "FLASH_LITE", "thinking_level": "LOW"},
    "report_generation": {"model_key": "PRO", "thinking_level": "MEDIUM"},
}
