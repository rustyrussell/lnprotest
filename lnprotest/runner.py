from typing import Any, Optional, List, Callable


class Choice:
    def __init__(self, value: Any, parent: Optional['Choice']):
        # Our value to return from the choose() call.
        self.value = value
        # Our children
        self.children: List['Choice'] = []
        # The parent (we assume a tree, not a DAG, so just one)
        self.parent = parent
        # Have we fully explored this and its children?
        self.is_finished = False

    def add(self, subvalue: Any) -> 'Choice':
        """Add a new choice to this node"""
        sub = Choice(subvalue, self)
        self.children.append(sub)
        return sub

    def mark_finished(self) -> None:
        """This leaf node is finished, mark parents finished as appropriate"""
        self.is_finished = True
        # If all siblings finished, parent is now finished
        if self.parent:
            if all([child.is_finished for child in self.parent.children]):
                self.parent.mark_finished()


class Runner:
    def __init__(self, path: Optional[List[Any]] = None):
        # Our total map of choices as they call .choose.
        self.root = Choice(None, None)
        self.current = self.root
        # If we're running a particular path, stick to this
        self.path = path

    def run_start(self) -> bool:
        """If you want to run manually, this tells you there is more
        iteration to do"""
        return not self.root.is_finished

    def run_done(self) -> None:
        """And call this after calling your function, to update the map"""
        self.current.mark_finished()
        self.current = self.root

    def run(self, func: Callable[['Runner', Any], Any],
            *args: Any, **kwargs: Any) -> bool:
        """Helper function to run func() until all iterations done or
        func returns False"""
        while self.run_start():
            if func(self, *args, **kwargs) is False:
                return False
            self.run_done()
        return True

    def choose(self, choices: Any = [True, False]) -> Any:
        """For clients to make a choice of which path to take"""
        if len(choices) < 2:
            raise ValueError("Need at least two choices to have a choice")

        if self.path is not None:
            assert self.path[0] in choices
            return self.path.pop(0)

        if self.current.children == []:
            for c in choices:
                self.current.add(c)

        # Determinism please: same previous choices must lead us to
        # the same choice!
        assert [c.value for c in self.current.children] == choices

        for c in self.current.children:
            if c.is_finished:
                continue
            self.current = c
            return self.current.value

        raise AssertionError(f"We were already finished at {self.current}")

    def get_path(self) -> List[Any]:
        """Return the choices which lead to this point
        (usually, after run() failed"""
        def get_one(choice: Choice):
            """Recurse so we get backwards, root -> ... -> child"""
            if choice.parent is None:
                return []
            return get_one(choice.parent) + [choice.value]

        return get_one(self.current)
