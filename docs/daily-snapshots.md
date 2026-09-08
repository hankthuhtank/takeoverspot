# Daily snapshots and account controls

The database captures the public board every day at noon in `America/Chicago`, including daylight-saving changes. A unique date permits one record per day. The UTC cron covers both Central offsets and retries during the noon hour; normal capture runs at 12:00. An outage can delay a capture, and `captured_at` records the actual time rather than inventing a historical state.

GitHub Actions renders the saved board independently of any visitor's browser. Image processing starts after capture and may be delayed by runner availability. Retries use the saved data, not the current board. The renderer authenticates with short-lived GitHub OIDC tokens restricted to this repository, main branch, and dedicated workflow. No service credentials are stored in GitHub.

Each public image is a 1600-pixel square JPEG capped at 1 MiB (at most approximately 365 MiB/year of images). Copy/download produces PNG in the visitor's browser. Pending captures protect their referenced uploads from cleanup until the image is saved. Capture data and completed image references cannot be overwritten. The Daily Snapshots tab pages through the archive; it does not post to social media.

The first scheduled capture is September 9, 2026. The feature was installed after September 8's noon; no historical captures were fabricated.

## Owner account management

Admin → Accounts → Manage provides disable, restore, and eligible permanent deletion. The verified sole owner controls this endpoint; the owner account is protected. Disabling bans authentication and blocks checkout creation, artwork changes, saved-design writes, and uploads even with an existing session. Existing artwork and financial records remain intact.

Permanent deletion requires the target email and explicit DELETE confirmation. Accounts with board ownership, checkout attempts, billing records, legacy bids/wins, or owned uploads must be disabled instead. A database deletion trigger independently prevents deletion of protected accounts. Actions are audited. No existing accounts were disabled or deleted during deployment.

Validation: 66 automated tests, interaction and manual-snapshot smoke checks, rolled-back database checks for owner protection and snapshot immutability, and an anonymous renderer request rejected with HTTP 401. The production render workflow also exercises Chromium, combined artwork, fonts, image dimensions, and JPEG output before processing pending records.
