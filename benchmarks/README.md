# Offline benchmark

This directory defines a data contract and a reproducible calculator for video-ad experiments. It does not contain live platform data or claim a winning creative.

## Data contract

Each row represents one asset or variant for one campaign and must include:

- `campaign_id`, `asset_id`, `platform`, `objective`, `audience`
- `spend`, `impressions`, `clicks`, `conversions`, `revenue`
- `data_status`: `synthetic`, `measured`, or `unverified`
- `attribution_window`, `date_range`, and `source` when available

Optional production fields are `production_cost`, `human_edit_hours`, and `accepted_outputs`.

The calculator reports CTR, click-based CVR, CPC, CPA, ROAS, and accepted-output cost. A zero denominator produces `null`. It checks basic count consistency and flags the first two rows as non-comparable when platform, objective, audience, or attribution window differs.

## Run locally

```bash
python3 scripts/benchmark.py benchmarks/sample-campaigns.json --output /tmp/benchmark.md
python3 scripts/benchmark.py benchmarks/sample-campaigns.json --format json
```

Synthetic rows are teaching fixtures. Replace them with an exported, permissioned dataset before making a business claim.
