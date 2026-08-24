# Distributed Identification Engine

Candidate realizations are partitioned deterministically into numbered shards. Each shard can be evaluated independently, permitting horizontal distribution across nodes and process-level parallelism inside a node.

## Execution record

Every shard returns one of:

- `completed`, with its ordered evaluation results;
- `failed`, with a serialized error record.

Aggregation is always sorted by `shard_id`, never completion order.

## Fault tolerance

A failed shard does not destroy completed results. The global result is explicitly marked incomplete, however. `merge_strict` refuses to promote a partial search into a complete candidate evaluation.

A scheduler or external distributed runtime can therefore retry only failed shard identities without repeating successful work.

## Identification invariant

Distributed execution changes computational placement, not the mathematical candidate space. A globally complete evaluation must be equivalent to serial evaluation over the same ordered candidate population.
