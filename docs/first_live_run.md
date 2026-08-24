# First Live Retrieval Run

The first empirical run executes all 416 required nation-year-feature retrievals concurrently and records the result of each cell.

A cell is valid only if its bound provider retrieval returns a numeric value after all declared transformations.

The run report contains:

- admission status;
- number of required cells (416);
- number of retrieved numeric cells;
- exact missing cells;
- exact retrieval errors by cell;
- SHA-256 checksum when and only when admission succeeds.

The report is diagnostic. It does not certify an empirical snapshot by itself. Certification remains delegated to the existing snapshot manifest gate.
