from __future__ import annotations

import argparse
from pathlib import Path

from fournations.concrete_sdmx_fetchers import ConcreteSDMXFetchers
from fournations.end_to_end import bound_provider_keys
from fournations.imf_worldbank_fetchers import IMFAdapter, make_imf_fetcher, make_world_bank_fetcher
from fournations.live_admission_runner import run, write_report
from fournations.live_cell_fetcher import make_live_cell_fetcher
from fournations.live_providers import WorldBankAdapter
from fournations.provider_transports import UrlTransport


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    transport = UrlTransport()
    imf = make_imf_fetcher(IMFAdapter(transport))
    world_bank = make_world_bank_fetcher(WorldBankAdapter(transport))
    fetcher = make_live_cell_fetcher(
        imf=imf,
        world_bank=world_bank,
        sdmx=ConcreteSDMXFetchers(transport),
    )

    payload = run(
        fetcher,
        experiment_id="institutional-hosts-usa-che-fra-ind-v1",
        provider_keys=bound_provider_keys(),
    )
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_report(path, payload)


if __name__ == "__main__":
    main()
