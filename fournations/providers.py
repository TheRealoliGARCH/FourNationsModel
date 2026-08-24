from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlencode
from urllib.request import urlopen
import json
from .empirical import FunctionalAdapter, Observation, Registry

PROVIDERS = ('IMF','WORLD_BANK','BIS','OECD')

@dataclass(frozen=True)
class ProviderRequest:
    series_id: str
    economies: tuple[str,...]=()
    start: str|None=None
    end: str|None=None
    options: Mapping[str,str]|None=None

def empty_registry() -> Registry:
    r=Registry()
    for p in PROVIDERS: r.register(FunctionalAdapter(p, lambda request, p=p: ()))
    return r

def rows(provider: str, raw: Iterable[Mapping[str,object]]) -> tuple[Observation,...]:
    return tuple(Observation(str(x.get('source',provider)),provider,str(x['series_id']),str(x['economy']),str(x['period']),float(x['value']),None if x.get('unit') is None else str(x['unit']),dict(x.get('metadata',{}))) for x in raw)

class WorldBankAdapter:
    provider='WORLD_BANK'; base_url='https://api.worldbank.org/v2'
    def fetch(self, request: Mapping[str,Any]) -> Iterable[Observation]:
        countries=';'.join(request['countries']); indicator=request['indicator']; params={'format':'json','per_page':1000}
        if request.get('date'): params['date']=request['date']
        url=f'{self.base_url}/country/{countries}/indicator/{indicator}?{urlencode(params)}'
        with urlopen(url,timeout=30) as h: payload=json.load(h)
        for row in (payload[1] if isinstance(payload,list) and len(payload)>1 else []):
            if row.get('value') is not None:
                yield Observation(url,self.provider,indicator,row['countryiso3code'],str(row['date']),float(row['value']),row.get('unit') or None,{'indicator_name':row['indicator']['value']})

class IMFDataMapperAdapter:
    provider='IMF'; base_url='https://www.imf.org/external/datamapper/api/v1'
    def fetch(self, request: Mapping[str,Any]) -> Iterable[Observation]:
        indicator=request['indicator']; economies=','.join(request['countries']); periods=','.join(str(x) for x in request.get('periods',()))
        url=f'{self.base_url}/{indicator}/{economies}' + (f'?{urlencode({"periods":periods})}' if periods else '')
        with urlopen(url,timeout=30) as h: payload=json.load(h)
        for economy, series in payload.get('values',{}).get(indicator,{}).items():
            for period,value in series.items():
                if value is not None: yield Observation(url,self.provider,indicator,economy,str(period),float(value))

class SDMXRequestAdapter:
    def __init__(self, provider: str, loader): self.provider=provider.upper(); self.loader=loader
    def fetch(self, request: Mapping[str,Any]) -> Iterable[Observation]: return self.loader(request)
