from abc import ABC, abstractmethod

Serializable = int | float | str | bool | None | list["Serializable"] | dict["Serializable", "Serializable"]

class ISerializable(ABC):
    @abstractmethod
    def serialize(self) -> Serializable:
        pass
