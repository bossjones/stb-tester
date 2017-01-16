import random
import time

from stbt import wait_until


def f(spec):
    """Helper function for wait_until selftests. Creates a function that returns
    the specified values one by one (10ms apart) each time it is called.

    Values are specified as space-separated characters. `.` means `None` and
    `F` means `False`.

    >>> g = f("F a b")
    >>> [g(), g(), g(), g(), g()]
    [False, 'a', 'b', False, 'a']
    """
    mapping = {".": None, "F": False}
    values = [mapping.get(x, x) for x in spec.split()]
    i = [0]

    def inner():
        time.sleep(0.01)
        if i[0] < len(values):
            v = values[i[0]]
            i[0] += 1
            return v
        else:
            i[0] = 1
            return values[0]

    return inner


def test_that_wait_until_returns_on_success():
    assert wait_until(f(". a b")) == "a"
    assert wait_until(f("F a b")) == "a"


def test_that_wait_until_times_out():
    start = time.time()
    assert wait_until(lambda: False, timeout_secs=0.1) is False
    end = time.time()
    assert 0.1 < end - start < 0.2


def test_that_wait_until_tries_one_last_time():
    assert wait_until(f("F T"), timeout_secs=0.01) == "T"
    assert wait_until(f("F F T"), timeout_secs=0.01) is False


def test_that_wait_until_tries_one_last_time_with_stable_secs():
    #                      stable_secs reached
    #           Timeout reached     |
    #                         |     |
    #                         v     v
    assert wait_until(f("a b b b b b b b b b b"),
                      timeout_secs=0.03, stable_secs=0.05) is None

    #                      stable_secs reached
    #           Timeout reached |
    #                         | |
    #                         v v
    assert wait_until(f("a b b b a a a a a a a"),
                      timeout_secs=0.03, stable_secs=0.02) == "b"


def test_that_wait_until_with_zero_timeout_tries_once():
    assert wait_until(lambda: True, timeout_secs=0)


def test_wait_until_stable_secs():
    random.seed(1)
    assert wait_until(random.random, timeout_secs=0.1)
    assert not wait_until(
        random.random, timeout_secs=0.1, stable_secs=0.01)

    assert wait_until(f("a b b")) == "a"
    assert wait_until(f("a b b"), timeout_secs=0.1, stable_secs=0.01) == "b"
    assert wait_until(f("a b c"), timeout_secs=0.1, stable_secs=0.01) is None


def test_wait_until_false_value():
    assert wait_until(f("F F F"), timeout_secs=0.1) is False
    assert wait_until(f("F F F"), timeout_secs=0.1, stable_secs=0.01) is None


def test_wait_until_falsey_value():
    class NonZero(object):
        def __nonzero__(self):
            return False

    value = wait_until(NonZero, timeout_secs=0.1)
    assert isinstance(value, NonZero)
