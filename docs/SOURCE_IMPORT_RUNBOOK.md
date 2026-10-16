# Full source import gate

The complete 87-file FCF v0.4.0 public-safe source ZIP (SHA-256 `85efa981d87eae498f15c752942ba94472f25a3773b66c44b0f63566a5e08044`) is not yet on this branch. Only the independently executable KBI bootstrap has been published.

To complete the import, validate archive hash, path safety, private-data redaction and license boundaries in an isolated checkout. Import the contents of its top-level folder on a review branch, run all 99 reference tests and schema checks, inspect remote Actions, review and merge. Do not tag a stable release or claim native OpenViking execution until those separate gates pass.
