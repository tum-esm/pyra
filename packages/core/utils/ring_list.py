class RingList:
    def __init__(self, max_size: float):
        assert max_size > 0, "a max_size of zero doesn't make any sense"
        self.__max_size: float = max_size
        self.__data: list[float] = [0] * max_size
        self.__current_index: int = -1  # -1 means empty

    def clear(self) -> None:
        """removes all elements"""
        self.__current_index: int = -1

    def append(self, x: float) -> None:
        """appends an element to the list"""
        self.__current_index += 1
        bounded_current_index = self.__current_index % self.__max_size
        self.__data[bounded_current_index] = x

    def get(self) -> list[float]:
        """returns the list of elements"""
        # list is full
        if self.__current_index >= (self.__max_size - 1):
            bounded_current_index = self.__current_index % self.__max_size
            return (
                self.__data[bounded_current_index + 1 : self.__max_size + 1]
                + self.__data[0 : bounded_current_index + 1]
            )

        # list is not empty but not full
        elif self.__current_index >= 0:
            return self.__data[0 : self.__current_index + 1]

        # list is empty
        return []

    def sum(self) -> float:
        """returns the max size of the list"""
        return sum(self.get())

    def set_maxsize(self, new_max_size: int) -> None:
        """sets a new max size"""
        current_list = self.get()
        self.__max_size = new_max_size
        self.__data = [0] * new_max_size
        self.__current_index = -1
        for item in current_list:
            self.append(item)

    def __str__(self) -> str:
        return str(self.__data__)
