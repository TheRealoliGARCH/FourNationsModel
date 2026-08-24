# ISG-BCI implementation

The theory defines an observation model $Y=S+\varepsilon$, a realization manifold

$$\mathcal M_r = \{D \in \mathcal D : R(D)=r\},$$

and a causal generator set $\mathcal G_C$. Identification occurs when

$$\mathcal F = \mathcal M_r \cap \mathcal G_C$$

contains exactly one signal. The paper states that, under this singleton condition, the infinite-sample posterior collapses to $\delta(S-S^*)$ and posterior entropy is zero.

## Computational interpretation

The first release uses a finite candidate approximation to $\mathcal M_r$. A candidate is a realization-generator vector. `RelationalStatistic` defines the observable map and a numerical distance to the observed relational statistic. `CausalConstraint` defines a membership test for $\mathcal G_C`.

The identification engine reports three states:

- `non_identified`: no candidate satisfies both the relational and causal restrictions;
- `set_identified`: two or more candidates remain feasible;
- `uniquely_identified`: exactly one candidate remains feasible.

This distinction is critical. The theory says unique identification produces $H=0$; the implementation does not infer $H=0$ merely because the optimizer converged.

## Numerical policy

High-precision verification uses `mpmath` with a configurable decimal precision. Fast candidate screening uses NumPy float64. Every decision carries an explicit residual tolerance and the result records the precision/tolerance used. Ill-conditioned feasible sets are flagged rather than hidden.

For nuclear/AAA-grade applications, the recommended workflow is:

1. screen candidates using float64;
2. re-evaluate surviving candidates at substantially higher precision;
3. perturb the tolerance over a predefined audit grid;
4. report whether the identification status is invariant;
5. fail closed when the status changes under admissible precision/tolerance perturbations.

## Next model layer

The next implementation step is the empirical generator system: construct nation-level and bilateral candidate generators from IMF/WB/BIS/OECD observables, then distribute candidate evaluation across nodes. The present package deliberately keeps that data-to-generator mapping separate from the mathematical identification engine.
