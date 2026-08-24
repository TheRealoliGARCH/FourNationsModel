# FourNationsModel

Computational implementation of *A Unified Theory of Monetary-Political-Economic Equilibrium*.

## Priority Stack

The first implementation layer is ISG-BCI identification, corresponding to Section 2 of the theory. The model treats observations as

$$Y = S + \varepsilon,$$

with Gaussian white noise, constructs an observational/relational representation, applies causal restrictions, and evaluates the feasible identification set

$$\mathcal F = \mathcal M_r \cap \mathcal G_C.$$

The theory's identification theorem assumes that this intersection contains one signal $S^*$; the implementation therefore reports the cardinality/geometry of the feasible set rather than silently asserting uniqueness. The theory also identifies posterior entropy collapse with unique identification. See the implementation notes in `docs/isg_bci.md`.

## Numerical design

- IEEE float64 is the default fast path.
- `mpmath` arbitrary precision is an optional high-precision path for ill-conditioned identification problems.
- Every numerical decision is accompanied by an explicit tolerance policy; tolerances are configuration, not magic constants.
- The implementation records condition numbers, residuals, precision, and tolerance used in every identification result.

## Parallel and distributed design

The identification layer is decomposed into deterministic, independently executable jobs. Local worker parallelism uses Python multiprocessing. Distributed execution is supported through a job interface so a cluster scheduler can partition realization candidates across nodes. Node failures are isolated at the job level and completed jobs remain usable.

The default implementation is deliberately scheduler-agnostic: Slurm, Kubernetes, Ray, Dask, or another runner can supply the outer distribution layer without changing the identification mathematics.

## Data adapters

Empirical data are represented through a source-neutral schema. Adapters are provided/planned for IMF, World Bank, BIS, and OECD datasets; raw downloads are kept separate from transformed model inputs so provenance is preserved.

## Development

```bash
python -m pip install -e .[dev]
pytest -q
```
