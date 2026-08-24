import numpy as np

from fournations.isg_bci import CausalConstraint, RelationalStatistic
from fournations.tolerance import audit_tolerance, geometric_ladder


def statistic(value):
    return RelationalStatistic(
        value=np.asarray(value, dtype=float),
        map_fn=lambda x: x,
        distance_fn=lambda a, b: float(np.linalg.norm(a - b)),
    )


def test_stable_unique_identification_is_certified():
    cert = audit_tolerance(
        np.array([1.0]),
        [np.array([1.0]), np.array([1.1])],
        statistic([1.0]),
        [CausalConstraint("positive", lambda x: x[0] > 0)],
        ladder=geometric_ladder(1e-4, levels=3),
    )
    assert cert.stable
    assert cert.certificate_status == "certified"
    assert cert.classification_path == ("uniquely_identified",) * 3


def test_tolerance_sensitive_result_is_not_certified():
    cert = audit_tolerance(
        np.array([1.0]),
        [np.array([1.0]), np.array([1.00005])],
        statistic([1.0]),
        ladder=geometric_ladder(1e-4, levels=3, shrink=0.1),
    )
    assert not cert.stable
    assert cert.certificate_status == "unstable_tolerance_path"
    assert 1 in cert.boundary_indices


def test_ladder_escalates_precision():
    ladder = geometric_ladder(1e-6, levels=4, initial_digits=40, digits_step=20)
    assert [x.digits for x in ladder] == [40, 60, 80, 100]
