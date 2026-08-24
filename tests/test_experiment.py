from fournations.empirical import Observation, snapshot
from fournations.generator import FeatureSpec
from fournations.experiment import PilotSpec, run_pilot

def test_reproducible_four_nation_pilot_records_snapshot_identity():
    economies=('USA','GBR','FRA','DEU')
    obs=[]
    for i,e in enumerate(economies,1):
        obs.append(Observation('fixture','TEST','GDP',e,'2024',float(i)))
        obs.append(Observation('fixture','TEST','RATE',e,'2024',float(i+1)))
    data=snapshot('TEST',{'fixture':'four-nation'},obs)
    spec=PilotSpec(economies,'2024',(FeatureSpec('gdp','GDP'),FeatureSpec('rate','RATE')),{'gdp':(0.0,0.1),'rate':(0.0,)})
    result=run_pilot(data,spec)
    assert result.snapshot_checksum==data.checksum
    assert result.candidate_count==2
    assert result.tolerance.certificate_status in {'certified','unstable_tolerance_path','ill_conditioned'}
