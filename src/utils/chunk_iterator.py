from collections.abc import Iterable
from itertools import islice


def iterate_by_chunks(iterator: Iterable, chunk_size: int) -> Iterable:
    it = iter(iterator)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk
