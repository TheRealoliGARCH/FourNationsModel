from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.request import Request, urlopen

from .live_providers import ProviderError
from .sdmx_normalization import normalize_csv_observations


@dataclass(frozen=True)
class Response:
    status: int
    body: bytes
    content_type: str


class UrlTransport:
    """Minimal injectable HTTP transport with explicit response decoding."""

    def __init__(self, opener: Callable[..., Any] | None = None, timeout: float = 30.0):
        self._opener = opener or urlopen
        self.timeout = timeout

    def get(self, url: str, accept: str) -> Response:
        request = Request(url, headers={"Accept": accept})
        try:
            with self._opener(request, timeout=self.timeout) as response:
                status = getattr(response, "status", response.getcode())
                return Response(
                    status=int(status),
                    body=response.read(),
                    content_type=response.headers.get("Content-Type", ""),
                )
        except Exception as exc:
            raise ProviderError(f"HTTP retrieval failed: {exc}") from exc

    def get_json(self, url: str) -> object:
        response = self.get(url, "application/json")
        if response.status != 200:
            raise ProviderError(f"HTTP status {response.status}")
        try:
            return json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("invalid JSON response") from exc

    def get_csv_observations(self, url: str) -> dict[str, list[dict[str, object]]]:
        response = self.get(url, "text/csv")
        if response.status != 200:
            raise ProviderError(f"HTTP status {response.status}")
        try:
            text = response.body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProviderError("invalid UTF-8 CSV response") from exc
        return normalize_csv_observations(text)
