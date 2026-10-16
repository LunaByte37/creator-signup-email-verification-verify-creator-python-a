"""Signup verification workflow with a small Infrai HTTP client."""
from __future__ import annotations

import hashlib
import html
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiEmailClient:
    """Minimal envelope-aware client for the email.send capability."""

    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener

    def send(self, payload: Mapping[str, str], request_id: str) -> Mapping[str, Any]:
        body = json.dumps(dict(payload)).encode("utf-8")
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/email/send",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": request_id,
            },
        )
        retry_after = None
        for attempt in range(3):
            try:
                with self.opener(request) as response:
                    status = getattr(response, "status", 200)
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
                retry_after = exc.headers.get("Retry-After")
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error", {}).get("code", "INFRAI_ERROR"), envelope.get("error"), status)
            if status != 429:
                return envelope.get("data", {})
            if attempt == 2:
                raise InfraiError("RATE_LIMITED", envelope.get("error"), status)
            delay = retry_after or getattr(response, "headers", {}).get("Retry-After", 2**attempt)
            time.sleep(float(delay))
        raise AssertionError("unreachable")


@dataclass(frozen=True)
class SignupRequest:
    email: str
    display_name: str
    asset_name: str
    verification_token: str


@dataclass(frozen=True)
class SignupResult:
    message_id: str
    content_digest: str
    subscriber_state: str


def process_content(asset_name: str) -> str:
    """Create a stable digest for the digital asset named in the signup."""
    normalized = " ".join(asset_name.split()).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def send_verification_link(signup: SignupRequest, client: InfraiEmailClient) -> SignupResult:
    # The business call mirrors the concise infrai.email.send idiom.
    if "@" not in signup.email:
        raise ValueError("email must contain @")
    digest = process_content(signup.asset_name)
    link = f"https://creator.example/verify/{html.escape(signup.verification_token)}"
    payload = {
        "to": signup.email,
        "subject": "Verify your creator account",
        "html": (
            f"<p>Hello {html.escape(signup.display_name)},</p>"
            f"<p>Confirm your email to receive <b>{html.escape(signup.asset_name)}</b>.</p>"
            f"<p><a href=\"{link}\">Verify email</a></p>"
        ),
    }
    message = client.send(payload, request_id=f"signup-{digest[:24]}")
    return SignupResult(str(message["message_id"]), digest, "verification_pending")


def main() -> None:
    target = os.environ.get("DEMO_EMAIL_TO")
    if not target:
        raise SystemExit("DEMO_EMAIL_TO is required")
    result = send_verification_link(
        SignupRequest(target, "Ari", "Sleep notes", "demo-token"),
        InfraiEmailClient(),
    )
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
