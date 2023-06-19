from lnprotest import Runner
from typing import List, Any


def singlefunc(runner: Runner, tracking: List[List[bool]]) -> None:
    """A simple test, should run twice"""
    tracking.append([runner.choose([True, False])])


def test_single():
    runner = Runner()
    tracking = []
    runs = []
    while runner.run_start():
        singlefunc(runner, tracking)
        runs.append(runner.get_path())
        runner.run_done()
        print(f"Path done: {runner.get_path()}")
        print(f"Tracking so far: {tracking}")

    assert runs == [[True], [False]]
    assert tracking == runs


def test_single_auto():
    """Test using runner.run()"""
    tracking = []
    assert Runner().run(singlefunc, tracking) is True
    assert tracking == [[True], [False]]


def test_twofunc():
    def twofunc(runner: Runner, tracking: List[List[Any]]) -> None:
        """A more complex, if first returns True should run that branch three times"""
        v1 = runner.choose([True, False])
        if v1:
            v2 = runner.choose(['A', 'B', 'C'])
            tracking.append([v1, v2])
        else:
            tracking.append([v1])

    tracking = []
    assert Runner().run(twofunc, tracking) is True
    assert tracking == [[True, 'A'], [True, 'B'], [True, 'C'], [False]]


def test_runnerfail():
    def fail(runner: Runner, tracking: List[List[bool]]) -> bool:
        """Test that returning False stops iteration"""
        choices = [runner.choose(), runner.choose(), runner.choose()]
        tracking.append(choices)
        return choices != [True, False, True]

    tracking = []
    runner = Runner()
    assert runner.run(fail, tracking=tracking) is False
    assert tracking == [[True, True, True], [True, True, False], [True, False, True]]
    assert runner.get_path() == [True, False, True]

    # Now force it along that path only
    newrunner = Runner(path=runner.get_path())
    tracking = []
    assert newrunner.run(fail, tracking) is False
    assert tracking == [[True, False, True]]


def test_dag():
    """Test that we do, in fact, turn a DAG into a tree.  You could argue that this is a bug, but it *is* more thorough."""
    def dag(runner: Runner, tracking: List[List[bool]]) -> None:
        choices = []
        choices.append(runner.choose())
        if choices[0]:
            choices.append(runner.choose())
        choices.append(runner.choose())
        tracking.append(choices)

    tracking = []
    assert Runner().run(dag, tracking) is True
    assert tracking == [[True, True, True],
                        [True, True, False],
                        [True, False, True],
                        [True, False, False],
                        [False, True],
                        [False, False]]
    
