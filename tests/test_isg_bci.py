import numpy as np

from fournations.isg_bci import CausalConstraint, RelationalStatistic, identify
from fournations.precision import PrecisionPolicy


def euclidean(a, b):
    return float(np.linalg.norm(a - b))


def test_unique_identification():
    target = np.array([1.0, 2.0, 3.0])
    relational = RelationalStatistic(target, lambda x: x, euclidean)
    candidates = [target, np.array([1.0, 2.0, 3.1])]
    result = identify(
        target,
        candidates,
        relational,
        causal_constraints=[CausalConstraint("positive", lambda x: np.all(x > 0))],
        policy=PrecisionPolicy(residual_tol=1e-12),
    )
    assert result.unique
    assert result.status == "uniquely_identified"
    assert result.posterior_entropy == 0.0


def test_set_identification_is_not_silently_collapsed():
    target = np.array([1.0, 1.0])
    relational = RelationalStatistic(target, lambda x: np.array([x[0] ** 2, x[1]]), euclidean)
    candidates = [np.array([1.0, 1.0]), np.array([-1.0, 1.0])]
    result = identify(target, candidates, relational)
    assert not result.unique
    assert result.status == "set_identified"
    assert result.posterior_entropy is None


def test_causal_restriction_can_restore_uniqueness():
    target = np.array([1.0, 1.0])
    relational = RelationalStatistic(target, lambda x: np.array([x[0] ** 2, x[1]]), euclidean)
    candidates = [np.array([1.0, 1.0]), np.array([-1.0, 1.0])]
    result = identify(
        target,
        candidates,
        relational,
        causal_constraints=[CausalConstraint("positive-first-coordinate", lambda x: x[0] > 0)],
    )
    assert result.unique
    assert result.posterior_entropy == 0.0


def test_tight_residuals_are_recorded():
    target = np.array([1.0, 2.0])
    relational = RelationalStatistic(target, lambda x: x, euclidean)
    result = identify(target, [target], relational, policy=PrecisionPolicy(residual_tol=1e-14))
    assert result.tolerance == 1e-14
    assert result.precision_digits >= 32
