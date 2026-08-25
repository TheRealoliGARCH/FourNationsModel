# PR 30 scope

Concrete BIS and OECD SDMX retrieval is isolated in `fournations/concrete_sdmx_fetchers.py`.

The implementation preserves the existing declared series bindings and routes raw CSV through the canonical observation normalization and completeness checks. No missing observation is interpolated or replaced.
