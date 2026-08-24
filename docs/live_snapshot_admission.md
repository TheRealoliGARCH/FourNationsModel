# Live Snapshot Admission

The `host-nations-v2` empirical panel is admitted only when every required nation-year-feature cell exists after all declared provider transformations.

The required tensor is:

- 4 nations: USA, CHE, FRA, IND;
- 13 calendar years: 2012 through 2024;
- 8 features;
- 416 required cells.

A missing raw provider observation, Swiss credit component, or required month for annualized monthly data blocks the entire snapshot.

On successful admission, the canonical ordered cell payload is hashed with SHA-256. The manifest records the experiment identifier, shape, checksum, exact provider keys, and retrieval timestamp.

No identification result may cite a snapshot manifest unless its admission status is `ready_for_snapshot`.
