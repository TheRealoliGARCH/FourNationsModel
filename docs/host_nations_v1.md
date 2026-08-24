# Host Nations V1: Empirical Feature Schema

The first substantive experiment fixes the nation set to USA, CHE, FRA and IND and uses annual observations from 2000 through 2024.

## Design principle

The first pass uses a deliberately small macro-financial state vector. The objective is identification and reproducibility, not maximal feature coverage.

The state vector contains:

1. IMF/WEO real GDP growth;
2. IMF/WEO consumer-price inflation;
3. IMF/WEO current-account balance as a share of GDP;
4. IMF/WEO general-government gross debt as a share of GDP;
5. World Bank GDP in current US dollars, transformed by logarithm;
6. BIS credit to the non-financial sector relative to GDP;
7. BIS real effective exchange-rate index, transformed by log difference;
8. OECD harmonised long-term interest rate where coverage permits.

## Alignment

All observations are annual. A model year is executable only when all four nations and all required features are available after provider-specific extraction. Missing values fail closed; the first experiment performs no imputation.

## Standardisation

Each feature is standardised cross-sectionally within year. The four-nation geometry therefore represents relative configuration rather than raw unit scale. A zero-variance feature fails closed because its z-score geometry is undefined.

## Candidate geometry

The baseline generator is perturbed symmetrically by -1%, 0% and +1% along declared candidate dimensions. The exact candidate dimensions and causal restrictions must be recorded before execution.

## Interpretation

A completed run establishes only the identification status for this declared experiment. It does not constitute confirmation of the underlying theory. Reproduction requires the experiment specification, provider requests, frozen source snapshots, candidate construction, causal restrictions and tolerance certificate.
