from fournations.parallel import run_parallel


def square(x):
    return x * x


def fail_on_two(x):
    if x == 2:
        raise RuntimeError("intentional")
    return x


def test_parallel_execution_preserves_order():
    results = run_parallel([1, 2, 3], square, max_workers=2)
    assert [r.value for r in results] == [1, 4, 9]
    assert all(r.ok for r in results)


def test_worker_failure_is_isolated():
    results = run_parallel([1, 2, 3], fail_on_two, max_workers=2)
    assert results[0].ok and results[0].value == 1
    assert not results[1].ok
    assert results[2].ok and results[2].value == 3
