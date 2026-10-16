# FCF provenance lineage (logical schema extension proposal)

## Entities

- `Origin`: identifier of GitHub repository / Drive file / source system.
- `Revision`: commit SHA or connector-supplied revision string.
- `ObservedSource`: immutable byte snapshot and FCF record hash.
- `DerivedClaim`: separately versioned statement citing source record hashes.
- `Assessment`: structural decision citing proposal digest.
- `HumanApproval`: **future authenticated** event, deliberately absent from P01.

## Edges and constraints

`Origin --hasRevision--> Revision --capturedAs--> ObservedSource`  
`DerivedClaim --cites--> ObservedSource`  
`Assessment --examines--> DerivedClaim`

Every edge carries its source evidence, actor origin, timestamp and source digest in future revisions. The present code verifies proposal-to-source record associations but does not cryptographically sign the edges or resolve actual ontology identities.

### Scientific method boundary

An asserted relationship `theorem -> proves -> hypothesis` is not created merely because it is present in a generated knowledge graph. Proof edges require externally checked proof artifacts; semantic similarity is insufficient.
