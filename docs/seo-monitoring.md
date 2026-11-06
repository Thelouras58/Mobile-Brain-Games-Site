# SEO monitoring operations

The repository has two different safeguards:

- `bundle exec rake test` builds and validates the local rendered artifact. Pull requests and the Pages deployment use this same command. The artifact uploaded for deployment is the artifact that passed validation.
- `bundle exec rake smoke` makes read-only requests to critical production pages. It retries transient failures and checks status, canonical tags, accidental `noindex`, and store-link URL structure.

## Automated production checks

`.github/workflows/monitor-site.yml` runs every day at 05:17 UTC and can also be started manually. Scheduled workflows only run from the repository's default branch, so the schedule remains inactive while this change exists only on a feature branch. GitHub Actions reports failures through its normal check and notification interface; no external credentials or messaging integrations are required.

The smoke check does not log in to Search Console or analytics, does not request indexing, and does not modify production. Store destinations are checked for valid HTTPS URL structure during release validation. The scheduled workflow also runs a separate retried external-store availability job with `continue-on-error`; bot blocking or temporary store outages are reported without blocking deployment or hiding the core website-smoke result.

## Weekly manual search review

Every Monday at 10:00 Europe/Athens, review the last 28 complete days against the preceding 28 in Search Console:

1. Confirm the report's latest complete date and filters.
2. Review clicks, impressions, CTR, and average position for priority product and browser pages.
3. Segment material changes by query, country, and device before attributing them to a release.
4. Inspect current indexing and Google-selected canonicals for priority URLs when an issue appears.
5. Record the observation, evidence, owner, and next review date in the project change log.

Investigate a matched-period decline when it is both at least 25 percent and at least 10 clicks. Treat Google generative-AI impressions as a separate monthly visibility signal; they are not clicks and must not be added to normal Search totals.

## Deployment and incident procedure

After deployment, run the production smoke check and confirm representative analytics events in the available analytics debugger. A persistent critical-page 4xx/5xx, unexpected `noindex`, wrong canonical, or broken store link requires same-business-day investigation. Confirmed loss of indexing for a priority product requires investigation within one business day.

The custom `404.html` is expected to be served with HTTP 404 by GitHub Pages. The rendered validator confirms its content and `noindex`; the HTTP status must be confirmed against the deployed site because a local static file server may return 200.
