from collections.abc import Callable, Hashable, Iterable


def remove_duplicates[T](it: Iterable[T], identity: Callable[[T], Hashable]) -> Iterable[T]:
    visited = set()

    for x in it:
        ident = identity(x)
        if ident not in visited:
            yield x

        visited.add(ident)
