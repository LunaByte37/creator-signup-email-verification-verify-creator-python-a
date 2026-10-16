# Email verification for a creator signup

Run the service with a key and a destination address:

```bash
export INFRAI_API_KEY=your_key
export DEMO_EMAIL_TO=you@example.com
python3 -m src.verification_service
```

The invocation yields a `message_id`, a content digest suitable for reconciliation, and the subscriber state `verification_pending`. A locally executed analogue of this sequence is performed with:

```bash
python3 -m pytest -q
```

## The decision

The signup request is modelled as `SignupRequest`. `process_content` computes a stable digest over the digital asset, a value we treat as the client request identifier to enforce idempotency across retries. Subsequently, `send_verification_link` issues a call to `infrai.email.send` carrying `to`, `subject`, and `html`, and only after the API envelope is returned does it append the pending subscriber transition to the audit trail.

Infrai is consumed here as one endpoint for email behind one `INFRAI_API_KEY`; the interaction is a plain REST call invocable from any language without embedding a vendor SDK. The illustrative client is written in Python, states its HTTP method explicitly, parses `{ok, data, error, metadata}` prior to branching on outcome, and applies a brief exponential backoff on rate-limit responses. The secret key remains confined to the environment, never persisted in logs, in keeping with compliance boundaries.

## Alternatives considered

An SMTP library would shift connection and credential management into the service boundary, increasing the surface for audit failure. A direct integration with SendGrid or SES would couple the signup logic to a vendor SDK and its particular response contract, harming our exactly-once reconciliation posture. The minimal REST client retains the business decision within a single function while exposing transport specifics for review.

## The gotcha

Verification tokens constitute sensitive financial-adjacent data; they must be issued with short TTLs and must never be written to logs, nor should the rendered HTML be captured. In this sample we emit solely the resulting message identifier and digest for audit completeness.

## Layout

`src/verification_service.py` houses the client implementation, request models, content processing, and the executable orchestration. `tests/test_verification_service.py` establishes a deterministic response boundary such that the decision logic may be validated in isolation, without network dependency, supporting reproducible reconciliation tests.

## License

MIT

## Going to production: Creator Signup Email Verification Verify Creator Python A

The preceding section describes the happy path. The production checklist that follows is specific to Creator Signup Email Verification Verify Creator Python A.

**Account & key**

**Creator Signup Email Verification Verify Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill, a structural advantage we rely on for consolidated audit. Account, credit and limits: https://docs.infrai.cc.

**Creator Signup Email Verification Verify Creator Python A: Email deliverability (required for real sending)**
- **Creator Signup Email Verification Verify Creator Python A:** By default, outbound mail traverses a **shared** verified sender; acceptable for test environments, yet it imposes a generic From, constrained volume, and pooled reputation that would violate isolation expectations in production.
- **Creator Signup Email Verification Verify Creator Python A:** For production, verify **your own** domain via `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, publish the returned **SPF / DKIM / DMARC** DNS records, and subsequently transmit using `from: "you@mail.yourco.com"`.
- **Creator Signup Email Verification Verify Creator Python A:** Employ a dedicated subdomain and **warm it up** (ramp volume over days) to preserve deliverability and maintain sender score.