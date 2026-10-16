# Source authority model

| Class | Example | v0.1 treatment |
|---|---|---|
| External source | GitHub file at exact commit | `OBSERVED`; not authenticated by FCF |
| Connector export | Drive export bytes plus claimed revision | `OBSERVED`; connector attestation is out-of-scope |
| OpenViking result | Vector-index hit with URI and abstract | `UNTRUSTED_RETRIEVAL` |
| Derived claim | LLM-proposed memory | `PROPOSED`, authority NONE |
| Structural assessment | Evidence and schema checks | `HOLD` or `ELIGIBLE_FOR_HUMAN_REVIEW` |
| Human-approved change | Future signed, identity-bound approval | NOT IMPLEMENTED |
| Canonical publication | Document/repo verified in authoritative source | NOT CREATED OR MODIFIED HERE |

Do not equate an OpenViking context URI with canonical project authority. The authoritative source remains the governed GitHub commit or Drive revision until an independent, documented promotion process changes that relationship.
