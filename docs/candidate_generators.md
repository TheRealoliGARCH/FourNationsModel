# Candidate Generator Layer

The empirical layer produces normalized observations. This layer maps those observations into a four-nation structural object.

## Construction

For each nation `i`, period `t`, and declared feature set `F`, construct

`S_i,t = (x_i,t,1, ..., x_i,t,m)`.

Exactly four states are required to construct a `Generator`:

`D_t = [S_1,t; S_2,t; S_3,t; S_4,t]`.

The layer rejects missing features, duplicate economies, inconsistent schemas, and any cardinality other than four.

## Candidate space

A base generator can be expanded over a declared perturbation grid. The perturbation mechanism is explicit and deterministic; no hidden optimizer noise is used to create candidates.

## Relational statistics

The initial library includes pairwise Euclidean-distance vectors and per-feature rank signatures. Additional statistics can be attached upstream of ISG-BCI without changing the empirical provider or identification layers.

## Invariant

Provider data determine observations. Feature specifications determine state construction. Candidate rules determine the realization space. Causal restrictions remain the responsibility of ISG-BCI.
