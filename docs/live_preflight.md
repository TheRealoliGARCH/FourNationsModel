# Live preflight execution

`host-nations-v2` is released only after exact metadata-resolved provider keys and complete 2012-2024 coverage are observed for every required nation-feature pair.

The live preflight records three states:

- `blocked_unresolved_metadata`
- `blocked_incomplete_coverage`
- `ready_for_snapshot`

BIS effective exchange rates are monthly. The experiment's declared transformation remains the calendar-year mean before construction of annual nation-state vectors. Exact series keys must be captured from provider metadata at execution time and stored with the frozen snapshot.

The implementation contains no fallback proxy and no automatic feature deletion.
