# Conflict-free PR review assignment

Reusable workflow: `.github/workflows/review-conflict-free.yml`.

## Rule

Request the configured reviewer only when the PR is open, not a draft, and GitHub explicitly reports `mergeable: true`. If mergeability is `null` after bounded retries, false, or otherwise unknown, do not request a review. Existing review requests are not duplicated. This workflow never merges a PR and does not change branch protection or required checks.

## Integration in a repository

After this workflow is merged into the `.github` repository's default branch, add a caller workflow to each repository that should use the policy:

```yaml
name: Conflict-free review assignment
on:
  pull_request:
    types: [opened, reopened, synchronize, ready_for_review]
permissions:
  contents: read
  pull-requests: write
jobs:
  request-review:
    if: github.event.pull_request.draft == false
    uses: A-TownChain-Okosystems/.github/.github/workflows/review-conflict-free.yml@main
    with:
      pull-request-number: ${{ github.event.pull_request.number }}
      reviewer: A-TownChain
    permissions:
      contents: read
      pull-requests: write
```

The caller must be installed in each target repository; files in the special `.github` repository do not automatically execute in every repository. The requested reviewer must have write access and be eligible to review in that repository. Keep the default reviewer unchanged unless the account's review eligibility has been confirmed.

## Evidence and rollout status

This change supplies the reusable implementation and integration contract. Organization-wide activation is not complete until caller workflows are present on the default branch of every intended active repository and their exact-head runs are verified. No automatic merge is permitted.
