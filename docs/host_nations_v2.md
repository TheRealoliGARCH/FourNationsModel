# host-nations-v2

`host-nations-v2` is a versioned successor to `host-nations-v1`.

## Reason for revision

The v1 experiment required an eight-feature annual panel from 2000 through 2024. Coverage evidence for OECD long-term interest rates for India does not support the full v1 window. The experiment is therefore not mutated in place.

## Window

The proposed window is 2012--2024, subject to exact provider metadata and final availability checks for every feature and nation.

## Invariants

- Four nations remain USA, CHE, FRA and IND.
- Eight features remain unchanged semantically.
- No interpolation or proxy substitution is allowed.
- Provider-specific keys must be metadata-resolved and recorded in the frozen snapshot.
- Failure of any feature-country-period cell blocks execution.

The v2 specification is a candidate experiment until the full panel passes the coverage gate and receives the `ready_for_snapshot` status.
