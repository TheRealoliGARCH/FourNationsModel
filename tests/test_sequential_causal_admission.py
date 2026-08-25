from fournations.bayesian_causal_membership import CausalEvidence, MembershipPrior
from fournations.membership import Candidate
from fournations.sequential_causal_admission import admit_posteriors, counterfactual_origin_effect, sequential_update


def test_sequential_evidence_updates_posterior_repeatedly():
    prior = MembershipPrior("IND", 0.5, origin_treatment=True)
    posterior = sequential_update(prior, (CausalEvidence("IND", 0.6, 0.4), CausalEvidence("IND", 0.7, 0.3)))
    assert posterior.posterior > 0.5
    assert posterior.origin_treatment is True


def test_empty_evidence_preserves_prior():
    prior = MembershipPrior("IND", 0.6, origin_treatment=True)
    posterior = sequential_update(prior, ())
    assert posterior.posterior == 0.6
    assert posterior.likelihood_ratio == 1.0


def test_counterfactual_origin_effect_is_explicit():
    evidence = (CausalEvidence("IND", 0.6, 0.4),)
    assert counterfactual_origin_effect(MembershipPrior("IND", 0.7, origin_treatment=True), MembershipPrior("IND", 0.5), evidence) > 0.0


def test_admission_remains_capped_at_four():
    names = ("A", "B", "C", "D", "E")
    posteriors = {name: sequential_update(MembershipPrior(name, 0.5), (CausalEvidence(name, 0.5 + index / 20, 0.5),)) for index, name in enumerate(names)}
    candidates = {name: Candidate(name, 1.0, 1.0) for name in names}
    state = admit_posteriors(posteriors, candidates)
    assert len(state.admitted) == 4
    assert state.admitted == ("E", "D", "C", "B")
