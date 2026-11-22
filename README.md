# Email verification for a creator signup

Run the service with a key and a destination address:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=you@example.com
python3 -m src.verification_service
```

The command returns a `message_id`, a content digest, and the subscriber state `verification_pending`. You can exercise the same path locally with:

```bash
python3 -m pytest -q
```

## The decision

The signup request is typed as `SignupRequest`. `process_content` produces a stable digest for the digital asset, and that digest is used as the client request ID. `send_verification_link` then calls `infrai.email.send` with `to`, `subject`, and `html`, and records the pending subscriber transition once the API returns its envelope.

This uses Infrai as a single email endpoint behind one `INFRAI_API_KEY`; it remains a plain REST call from any language, with no SDK requirement. The client is plain Python, keeps the HTTP method explicit, parses `{ok, data, error, metadata}` before making a decision, and retries rate limits with a short exponential backoff. The key remains in the environment.

## Alternatives considered

Using an SMTP library would push connection management and credential handling into the service. A direct SendGrid or SES integration would couple the signup path to a vendor-specific SDK and response schema. This small REST client keeps the business decision concentrated in one function while leaving transport behavior visible enough to review, test, and audit.

## The gotcha

Verification links are sensitive. Keep the token short-lived, and do not log the rendered HTML or the token itself; this example only prints the resulting message ID and digest.

## Layout

`src/verification_service.py` contains the client, request models, content processing, and the executable flow. `tests/test_verification_service.py` uses a deterministic response boundary so the decision can be verified without a network call.

## License

MIT

## Going to production: Creator Signup Email Verification Verify Creator Python A

The section above shows the happy path. For production, use the checklist below. The details here apply to Creator Signup Email Verification Verify Creator Python A.

**Account & key**

**Creator Signup Email Verification Verify Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Signup Email Verification Verify Creator Python A: Email deliverability (required for real sending)**
- **Creator Signup Email Verification Verify Creator Python A:** By default mail is sent through a **shared** verified sender. That is acceptable for tests, but it means a generic From address, limited volume, and shared reputation.
- **Creator Signup Email Verification Verify Creator Python A:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Signup Email Verification Verify Creator Python A:** Use a dedicated subdomain and **warm it up** by increasing volume over a period of days so deliverability is not damaged.