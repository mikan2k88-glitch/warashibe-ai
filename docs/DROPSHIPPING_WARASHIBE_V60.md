# Dropshipping Warashibe v6.0

## Endpoint

v6.0 completes the Limited Live Gate preparation layer under explicit Human Control.

The gate does not execute commerce.

## Milestones

### v5.5 Approval Intent

Creates a hashed, single-use approval intent with:

- approval ID
- product key
- maximum amount
- expiry
- Human Gate requirement

### v5.6 One-shot Contract

Binds an approval intent to a successful v5.4 preflight.

The contract is:

- single-use
- non-retryable
- external-write disabled

### v5.7 Receipt Evidence

Creates an appendable receipt that proves the current proof path remains:

- not executed
- no payment captured
- no supplier order created
- no external write performed

### v5.8 Recovery Plan

Requires:

- manual contact path
- supplier cancellation path
- known refund terms
- available kill switch
- assigned human support owner

Automatic cancellation and refund remain disabled.

### v5.9 Transition Gate

Requires:

- ready one-shot contract
- unused/non-executed receipt state
- recovery readiness
- clear kill switch

The only allowed next action is final human review.

### v6.0 Limited Live Gate

Combines:

- v5.4 preflight
- single-use approval intent
- one-shot contract
- receipt evidence
- recovery plan
- transition gate

Passing v6.0 means the package is ready for Human Control review only.

## Safety boundary

v6.0 does not enable:

- automatic execution
- external commerce writes
- automatic retry
- automatic cancellation
- automatic refund
- automatic promotion

The deterministic proof verifies Human Gate control remains mandatory.
