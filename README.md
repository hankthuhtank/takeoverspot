# TAKEOVER

**The webpage belongs to whoever wants it most.**

Production frontend for [takeoverspot.com](https://takeoverspot.com).

Backend: dedicated TAKEOVER Supabase project. Payments: Stripe Checkout.

## Responsive board — 1.1.0

The sixteen spots retain one square coordinate system. Header, board controls and legal links occupy their own layout rows, so wrapping controls never cover paid territory.

- **All 16:** fits the entire board inside the measured available space. Margins are intentional when a rectangular screen contains a square board.
- **Explore:** fills the available screen area with a larger board and native scrolling. The map shows the visible area and lets visitors jump to a numbered spot. Mouse dragging and keyboard arrows also work.
- **Zoom:** changes viewing scale without changing artwork, spot order, adjacency or ownership.
- **Artwork view:** enlarges a territory with its original frame and missing-cell mask. Its website link and the selected spot's current takeover price remain separate actions.
- **Canvas:** fits wide and tall territories inside both available dimensions. Editor and published text share the same formatting structure and proportional typography.

No database schema, payment endpoint, authentication configuration, or ownership rules change in this release. CSS loads in the document head to avoid a mismatched layout during startup.

### Validation

`node --test tests/board-layout.test.cjs` covers eleven viewport sizes, wrapped headers, zoom reachability and all sixteen rectangular territory proportions. `tests/interaction-smoke.cjs` uses jsdom 30.0.1 with mocked backend responses to exercise board navigation, combined artwork, preview-to-purchase, editor preview, partial territory loss and paused controls. CI installs that test dependency separately from the frontend.

These checks validate calculations and DOM behavior; they do not establish pixel-level rendering on Safari/Chrome or verify live Stripe transactions. Review on an actual phone and desktop before production rollout.
