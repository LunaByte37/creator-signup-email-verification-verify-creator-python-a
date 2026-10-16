import json

from src.verification_service import SignupRequest, send_verification_link


class FakeResponse:
    status = 200
    headers = {}

    def read(self):
        return json.dumps({"ok": True, "data": {"message_id": "msg_test"}}).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_signup_sends_verification_and_marks_pending():
    seen = {}

    def opener(request):
        seen["method"] = request.method
        seen["auth"] = request.headers["Authorization"]
        seen["body"] = json.loads(request.data)
        return FakeResponse()

    result = send_verification_link(
        SignupRequest("person@example.com", "Mina", "Course PDF", "token-7"),
        __import__("src.verification_service", fromlist=["InfraiEmailClient"]).InfraiEmailClient("test-key", opener),
    )
    assert result.message_id == "msg_test"
    assert result.subscriber_state == "verification_pending"
    assert seen["method"] == "POST"
    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["to"] == "person@example.com"
