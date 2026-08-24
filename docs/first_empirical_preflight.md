# First Empirical Preflight

The provider metadata preflight is a gate, not an empirical result.

## Resolved facts

The IMF WEO block and World Bank GDP indicator are explicitly bound. BIS credit is available as percentage of GDP, while the exact SDMX series keys remain metadata-resolved. OECD's current API exposes long-term interest rates through the KEI dataflow with measure `IRLT`; the selected four-country experiment must still demonstrate complete annual coverage for USA, CHE, FRA and IND.

## Current execution status

`blocked_pending_complete_coverage`

This status is intentional. The eight-dimensional experiment may run only after every required feature passes the common-window coverage check. If long-term government bond yields or another required series do not cover India, the experiment is not silently reduced to seven dimensions.

The next admissible action is either:

1. resolve an exact series with complete coverage while preserving the declared feature semantics; or
2. create a new experiment specification with an explicitly revised feature schema.

A failed coverage check is evidence about data availability, not evidence against the Four Nations theory.
