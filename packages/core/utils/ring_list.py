class RingList:
    """
    Base code created by Flavio Catalani on Tue, 5 Jul 2005 (PSF).
    Added empty(), sum(), and reinitialize() functions.

    https://code.activestate.com/recipes/435902-ring-list-a-fixed-size-circular-list/
    """

    def __init__(self, length: int):
        self.__max__: int = length
        self.__data__: list[int] = []
        self.__full__: int = 0
        self.__cur__: int = 0

    def empty(self) -> None:
        self.__data__ = []
        self.__full__ = 0
        self.__cur__ = 0

    def append(self, x: int) -> None:
        if self.__full__ == 1:
            for i in range(0, self.__cur__ - 1):
                self.__data__[i] = self.__data__[i + 1]
            self.__data__[self.__cur__ - 1] = x
        else:
            self.__data__.append(x)
            self.__cur__ += 1
            if self.__cur__ == self.__max__:
                self.__full__ = 1

    def get(self) -> list[int]:
        return self.__data__

    def remove(self) -> None:
        if self.__cur__ > 0:
            del self.__data__[self.__cur__ - 1]
            self.__cur__ -= 1

    def size(self) -> int:
        return self.__cur__

    def maxsize(self) -> int:
        return self.__max__

    def sum(self) -> int:
        return sum(self.get())

    def reinitialize(self, length: int) -> None:
        self.__max__ = length
        self.__full__ = 0
        self.__cur__ = 0
        handover_list = self.get()
        self.__data__ = []

        for item in handover_list:
            self.append(item)

    def __str__(self) -> str:
        return str(self.__data__)