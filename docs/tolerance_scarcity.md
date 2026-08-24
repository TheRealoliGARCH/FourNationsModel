# Tolerance Scarcity Layer

The Four Nations Model treats numerical tolerance as a scarce computational resource.

## Certification rule

Let `I(tau, p)` denote the identification classification obtained at residual tolerance `tau` and arithmetic precision `p`. A result is tolerance-certified only when, over a predeclared ladder,

`I(tau_1, p_1) = ... = I(tau_K, p_K)`

and the feasible support cardinality is invariant.

The implementation uses a geometric tolerance ladder and an increasing precision ladder. The same candidate population is reused at every rung.

## Certificate states

- `certified`: classification and support cardinality are invariant and no rung is ill-conditioned.
- `unstable_tolerance_path`: tightening tolerance changes the identification outcome.
- `ill_conditioned`: identification remains numerically ill-conditioned at one or more rungs.

## Boundary cases

A boundary case is accepted under the loosest tolerance but rejected under the tightest tolerance. Such cases are returned explicitly for higher-precision or alternative-model review.

This layer is deliberately upstream of equilibrium optimization. A downstream solver must not treat a tolerance-sensitive identification result as structural knowledge.
