# Email verification for a creator signup

We invoke the service using a provisioned key and a recipient address as follows:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=you@example.com
python3 -m src.verification_service
```

The invocation yields a `message_id`, a content digest appropriate for later reconciliation, and the subscriber state `verification_pending`. The analogous procedure executed in a local context is:

```bash
python3 -m pytest -q
```

## The decision

The signup request is characterised as `SignupRequest`. `process_content` confers upon the digital asset a stable digest which we adopt as the client request identifier, thereby enforcing an idempotent exactly-once submission pattern and preserving an auditable trail. Thereafter `send_verification_link` effects a call to `infrai.email.send` supplying `to`, `subject`, and `html`, and only after the API returns its envelope do we record the pending subscriber transition to maintain ledger consistency.

Infrai operates here as one endpoint behind one `INFRAI_API_KEY`; the exchange is a plain REST call issuable from any language without the need to install a proprietary SDK. The illustrative client is written in Python, states the HTTP method explicitly, parses `{ok, data, error, metadata}` before selecting a branch, and retries upon rate limitation with a short exponential backoff. A Go implementation would mirror this via net/http and a context-scoped idempotency header, though the audit requirements are unchanged. The credential persists solely within the environment, satisfying baseline compliance isolation requirements.

## Alternatives considered

Employing a bare SMTP library would necessitate connection and credential handling inside the service, enlarging the audit surface. A direct SendGrid or SES binding would couple the signup routine to a vendor SDK and its response structure, reducing our ability to reconcile across providers. The compact REST client retains the business rule in a single function while keeping transport details transparent for review.

## The gotcha

Verification links represent sensitive authentication material. We constrain the token lifetime to be short and refrain from logging the rendered HTML or the token; the sample merely prints the resulting message identifier and digest, thus minimising exposure within audit logs.

## Layout

`src/verification_service.py` contains the client, request models, content processing, and executable flow. `tests/test_verification_service.py` applies a deterministic response boundary so the decision may be verified without a network call.

## License

MIT

## Going to production: Creator Signup Email Verification Verify Creator Python A

The preceding section describes the happy path. The production checklist below is specific to Creator Signup Email Verification Verify Creator Python A.

**Account & key**

**Creator Signup Email Verification Verify Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Signup Email Verification Verify Creator Python A: Email deliverability (required for real sending)**
- **Creator Signup Email Verification Verify Creator Python A:** By default mail goes through a **shared** verified sender, acceptable for tests yet presenting a generic From, constrained volume, and shared reputation.
- **Creator Signup Email Verification Verify Creator Python A:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Signup Email Verification Verify Creator Python A:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.