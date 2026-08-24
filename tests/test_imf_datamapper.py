from fournations.imf_datamapper import IMFDataMapperAdapter


class FakeClient:
    def get_json(self, url):
        return {"values": {"NGDP_RPCH": {"USA": {"2012": 2.3, "2013": None, "2014": 2.5}}}}


def test_imf_datamapper_extracts_declared_window_without_filling_missing_values():
    adapter = IMFDataMapperAdapter(FakeClient())
    values = adapter.annual_series("NGDP_RPCH", "USA", 2012, 2014)
    assert values == {2012: 2.3, 2014: 2.5}
