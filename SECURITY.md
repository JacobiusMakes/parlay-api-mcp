# Security policy

This repository publishes the ParlayAPI MCP server. Please reproduce issues on
the latest published release when possible. There is no separate long-term
support branch or guaranteed response-time commitment.

Report vulnerabilities privately to **support@parlay-api.com**, the security
reporting address documented in the README. Include the affected release,
minimal reproduction steps and expected versus observed behavior. Remove API
keys, credentials, payment details and private account responses before sending.
Do not publish sensitive details in a public GitHub issue.

Public discovery does not require a key. Account tools use the operator's own
ParlayAPI account and allowance. Account creation, checkout-link creation,
login-link email and saved-book changes should be explicitly approved in the
MCP client. Tool discovery alone does not perform those actions.
