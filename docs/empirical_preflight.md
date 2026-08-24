# Empirical preflight

`host-nations-v1` separates confirmed series identifiers from SDMX selections that must be resolved against current provider metadata before retrieval.

## Confirmed bindings

- IMF WEO: `NGDP_RPCH`, `PCPIPCH`, `BCA_NGDPD`, `GGXWDG_NGDP`.
- World Bank WDI: `NY.GDP.MKTP.CD`.

## Provider-metadata resolution

BIS and OECD requests are not encoded as guessed positional SDMX keys. Before execution the adapter must:

1. retrieve the current dataflow and structure metadata;
2. resolve each named dimension selection to a concrete provider key;
3. record the resolved key and metadata version in the snapshot;
4. test coverage for USA, CHE, FRA and IND over 2000--2024.

The experiment fails closed if any required series lacks complete common coverage. In particular, the OECD long-term government bond yield must not be substituted or imputed merely to preserve an eight-dimensional state vector.

This preflight is part of the experiment definition: a series binding is reproducible only when both the semantic selection and the provider metadata version are preserved.
