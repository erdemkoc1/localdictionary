"""Strictly local neural translation adapter.

This module intentionally has no networking imports or package-manager logic.
It loads only model directories bundled with LocalDictionary and invokes
CTranslate2 plus SentencePiece directly.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import ctranslate2
import sentencepiece as spm

from src.utils import get_resource_path, get_short_path


class LocalNMTError(RuntimeError):
    """Raised when a bundled local model cannot be loaded or executed."""


@dataclass(frozen=True)
class _LoadedModel:
    translator: ctranslate2.Translator
    tokenizer: spm.SentencePieceProcessor


class LocalNMTEngine:
    """Thread-safe CPU-only loader for the bundled TR/EN model pairs."""

    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = Path(models_dir or get_resource_path(os.path.join("data", "models")))
        self._models: Dict[Tuple[str, str], _LoadedModel] = {}
        self._lock = threading.RLock()
        self._warmup_started = False

    def _find_package(self, from_code: str, to_code: str) -> Path:
        if (from_code, to_code) not in {("tr", "en"), ("en", "tr")}:
            raise LocalNMTError(f"Unsupported local language pair: {from_code}->{to_code}")
        if not self.models_dir.is_dir():
            raise LocalNMTError(f"Bundled model directory is missing: {self.models_dir}")

        for metadata_path in sorted(self.models_dir.glob("*/metadata.json")):
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if metadata.get("from_code") == from_code and metadata.get("to_code") == to_code:
                return metadata_path.parent

        raise LocalNMTError(
            f"Bundled model is missing for {from_code}->{to_code}. "
            "The application will use its offline rule-based fallback."
        )

    def _load_model(self, from_code: str, to_code: str) -> _LoadedModel:
        key = (from_code, to_code)
        with self._lock:
            cached = self._models.get(key)
            if cached is not None:
                return cached

            package_dir = self._find_package(from_code, to_code)
            model_dir = package_dir / "model"
            tokenizer_path = package_dir / "sentencepiece.model"
            if not model_dir.is_dir() or not tokenizer_path.is_file():
                raise LocalNMTError(f"Incomplete bundled model package: {package_dir.name}")

            model_path = get_short_path(str(model_dir))
            tokenizer_file = get_short_path(str(tokenizer_path))
            cpu_count = os.cpu_count() or 1
            intra_threads = max(1, min(4, cpu_count // 2 or 1))
            try:
                translator = ctranslate2.Translator(
                    model_path,
                    device="cpu",
                    compute_type="int8",
                    inter_threads=1,
                    intra_threads=intra_threads,
                )
                tokenizer = spm.SentencePieceProcessor(model_file=tokenizer_file)
            except Exception as exc:
                raise LocalNMTError(f"Could not load local {from_code}-{to_code} model") from exc

            loaded = _LoadedModel(translator=translator, tokenizer=tokenizer)
            self._models[key] = loaded
            return loaded

    def is_available(self, from_code: str, to_code: str) -> bool:
        try:
            self._find_package(from_code, to_code)
            return True
        except LocalNMTError:
            return False

    def warm_up(self):
        """Load both directions once in a background daemon thread."""
        if self._warmup_started:
            return
        self._warmup_started = True

        def _load() -> None:
            for direction in (("en", "tr"), ("tr", "en")):
                try:
                    self._load_model(*direction)
                except LocalNMTError:
                    pass

        threading.Thread(target=_load, name="localdictionary-nmt-warmup", daemon=True).start()

    def translate(self, text: str, from_code: str, to_code: str) -> str:
        text = text.strip()
        if not text:
            return ""
        if len(text) > 20_000:
            raise LocalNMTError("Input exceeds the safe 20,000 character limit")

        model = self._load_model(from_code, to_code)
        with self._lock:
            source_tokens = model.tokenizer.encode(text, out_type=str)
            if not source_tokens:
                return text
            try:
                results = model.translator.translate_batch(
                    [source_tokens],
                    beam_size=4,
                    max_batch_size=32,
                    batch_type="tokens",
                    replace_unknowns=True,
                )
                if not results or not results[0].hypotheses:
                    raise LocalNMTError("The local model returned no translation")
                translated = model.tokenizer.decode(results[0].hypotheses[0])
            except LocalNMTError:
                raise
            except Exception as exc:
                raise LocalNMTError("Local neural translation failed") from exc

        return translated.lstrip()
