# Coverage Resolution Protocol v2

`host-nations-v1` remains immutable and blocked pending exact eight-feature coverage.

## Resolution procedure

1. Query provider metadata and availability constraints for each unresolved semantic target.
2. Record the exact dataset/dataflow, key, frequency, unit and coverage interval returned by the provider.
3. Test the common intersection for USA, CHE, FRA and IND over 2000--2024.
4. If all eight features pass, execute `host-nations-v1` unchanged.
5. If any feature fails, create a successor experiment specification rather than mutating v1.

## Successor rule

A successor may replace an unavailable feature only when the replacement has the same declared economic concept or when the conceptual change is explicitly versioned and documented. No interpolation or silent proxy substitution is permitted.

## Current targets

- BIS: domestic credit to the non-financial sector as percent of GDP.
- BIS: broad real effective exchange rate, annualized from an explicitly recorded provider frequency.
- OECD: long-term government interest rate, annual percent, with complete coverage for all four nations.

The OECD SDMX API provides data-availability and structure endpoints and must be used to resolve exact keys rather than assuming positional keys.
