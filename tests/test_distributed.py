from fournations.distributed import execute, merge_strict, partition

def square(x): return x*x

def boom(x):
    if x == 5: raise ValueError('boom')
    return x

def test_partition_is_deterministic():
    shards = partition(list(range(7)), 3)
    assert [s.shard_id for s in shards] == [0,1,2]
    assert [s.candidates for s in shards] == [(0,1,2),(3,4,5),(6,)]

def test_parallel_results_are_merged_in_shard_order():
    result = execute(list(range(8)), square, shard_size=2, workers=2)
    assert result.complete
    assert merge_strict(result) == tuple(x*x for x in range(8))

def test_shard_failure_is_isolated():
    result = execute(list(range(8)), boom, shard_size=2, workers=2)
    assert not result.complete
    assert [x.shard_id for x in result.failures()] == [2]
