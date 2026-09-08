# Production audit — September 8, 2026

Reviewed the deployed Takeover checkout, webhook, refunds, reconciliation, recovery, login handoff, storage cleanup, email worker, support, admin console and launch health functions; database access, grants, policies, scheduled jobs, queues and live Stripe webhook configuration. This is a point-in-time audit, not a guarantee against future defects.

## Fixes shipped

- Checkout holds a consistent board state while calculating the quote and inserting its items. Per-user quote limiting is serialized.
- Checkout does not expose a Stripe payment URL until the session is recorded for recovery; a failed write attempts to expire that session.
- Housekeeping retains linked open checkouts for Stripe reconciliation instead of cancelling them solely because two hours elapsed. Payment-bearing records are excluded from unpaid-record pruning.
- Both scheduled and owner-triggered storage scans paginate every reference source, check exact counts, and stop on failed or incomplete reads. Retention configuration must load successfully. Tests cover references beyond the 1,000-row API cap.
- Health checks fail when database queries fail and flag reconciliation runs with attempt errors.
- Removed client execution grants on three trigger functions. Optimized saved-design RLS evaluation while preserving ownership rules.
- The owner console additionally requires exactly one owner record matching the verified user.
- Frontend purchasing fails closed when board or configuration reads are incomplete.

## Production evidence

- All inspected public and storage tables had RLS enabled. Payment finalization functions were service-only. Board reads expose public artwork columns, excluding private user/payment identifiers.
- Exactly one owner; authenticated clients cannot insert owner records.
- Live Stripe webhook enabled at the expected Supabase endpoint for Checkout completion. The handler validates the raw-body signature and timestamp. Checkout currently accepts cards.
- At inspection: no created/open/stale/refund-failed attempts; no pending/failed email queue rows. All five cron jobs had successful SQL invocations over 24 hours. Recent HTTP responses included three transient timeouts and 429 successful responses; latest reconciliation reported no errors. Cron success alone is not proof of worker success.
- New storage worker was checked using its read-only scan action, without deleting files.
- 61 automated tests plus DOM interaction and snapshot pipeline checks passed locally. Snapshot checks use a stub rasterizer; they do not replace Safari/iOS or signed-in owner clipboard testing.

## Remaining limitations and follow-up

- Supabase reports leaked-password protection disabled; password-bearing accounts exist. Enable this in Auth password security settings if supported by the project's plan. The available connector cannot change this setting. See https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection.
- Existing refund handlers infer success from Stripe's successful HTTP response; pending/failed asynchronous refund states and interrupted owner-refund requests need explicit status reconciliation. Admin health and Stripe should still be checked for refund exceptions. No live charge or refund was made during this audit.
- Public impression/click counters are approximate and can be inflated by repeated API requests; they are not verified audience counts.
- Cleanup pagination now fails safely on detected incomplete reads; reference reads and object deletion are not one atomic transaction. Historical artwork beyond configured retention may be removed when otherwise unreferenced.
- Provider outages, browser-specific export behavior, and future schema/configuration changes remain operational risks. Keep the launch gate and owner health checks in use.

## Snapshot

Owner console → Dashboard → Create Snapshot → Copy Image or Download PNG. Output is the complete 2048 × 2048 board, independent of the visible pan/zoom crop. Artwork, embedded fonts and combined-territory masks are retained; purchase controls and private console data are excluded. Animated layers become a still frame. Nothing is posted automatically.

The renderer is locally vendored html-to-image 1.11.13 with its MIT license. Google font fetches are restricted to the existing Google Fonts origins in CSP; no third-party screenshot service receives the board or account data.
