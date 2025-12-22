from typing import Protocol, runtime_checkable


@runtime_checkable
class AsyncClosable(Protocol):
    async def aclose(self) -> None:
        raise NotImplementedError
