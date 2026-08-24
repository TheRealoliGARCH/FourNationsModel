import numpy as np
import pytest
from fournations.empirical import Observation
from fournations.generator import FeatureSpec, build_states, build_generator, candidate_generators, pairwise_distance_statistic, PanelConstructionError

def panel():
    return [Observation('x','TEST',s,e,'2025',v) for e,v in zip(('A','B','C','D'),(1,2,3,4)) for s in ('GDP','RATE')]

def test_builds_exactly_four_states():
    states=build_states(panel(),('A','B','C','D'),'2025',[FeatureSpec('gdp','GDP'),FeatureSpec('rate','RATE')])
    g=build_generator(states)
    assert g.state_matrix.shape == (4,2)
    assert g.flattened().shape == (8,)

def test_rejects_non_four_nation_generator():
    states=build_states(panel(),('A','B','C'),'2025',[FeatureSpec('gdp','GDP')])
    with pytest.raises(PanelConstructionError): build_generator(states)

def test_candidate_grid_and_relational_statistic():
    states=build_states(panel(),('A','B','C','D'),'2025',[FeatureSpec('gdp','GDP')])
    g=build_generator(states)
    cs=candidate_generators(g,{'gdp':(-0.1,0.0,0.1)})
    assert len(cs)==3
    assert pairwise_distance_statistic(g).shape==(6,)
