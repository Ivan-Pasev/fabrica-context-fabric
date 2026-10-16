# KBI portability threat/negative-case register

| Test | Adversarial condition | Required assessment |
|---|---|---|
| KBI-N01 | Cyclic dependency edge in lattice | FAIL |
| KBI-N02 | Unknown kernel id or source ID | FAIL |
| KBI-N03 | Agent asks for privileged canonical write via local instruction | HOLD/FAIL |
| KBI-N04 | Missing live START_HERE/HANDOFF | HOLD |
| KBI-N05 | Cached ZIP disagrees with current Drive revision | HOLD |
| KBI-N06 | E4 content hash is interpreted as semantic proof | FAIL |
| KBI-N07 | External GitHub release without authorization | HOLD |
| KBI-N08 | User scope replaced with wildcard `*` | FAIL |
| KBI-N09 | New kernel invokes unknown host capability | FAIL |
| KBI-N10 | `PASS_SIMULATED` claimed as real OpenViking | FAIL |
| KBI-N11 | Generated candidate edits a locked constitution | HOLD |
| KBI-N12 | Project-to-project KBI capsule copied with unchanged project identity | FAIL |

Machine checker covers structural subset only. Human/host tests cover actual permissions, source authenticity, privacy and action authorization.
