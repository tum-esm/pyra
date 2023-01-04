class RingList:
    def __init__(self, max_size: int):
        assert max_size > 0, "a max_size of zero doesn't make any sense"
        self._max_size: int = max_size
        self._data: list[float] = [0 for _ in range(max_size)]
        self._current_index: int = -1  # -1 means empty

    def clear(self) -> None:
        """removes all elements"""
        self._current_index = -1

    def is_full(self) -> bool:
        """returns true if list is full"""
        return self._current_index >= (self._max_size - 1)

    def append(self, x: float) -> None:
        """appends an element to the list"""
        self._current_index += 1
        bounded_current_index = self._current_index % self._max_size
        self._data[bounded_current_index] = x

    def get(self) -> list[float]:
        """returns the list of elements"""
        # list is full
        if self._current_index >= (self._max_size - 1):
            bounded_current_index = self._current_index % self._max_size
            return (
                self._data[bounded_current_index + 1 : self._max_size + 1]
                + self._data[0 : bounded_current_index + 1]
            )

        # list is not empty but not full
        elif self._current_index >= 0:
            return self._data[0 : self._current_index + 1]

        # list is empty
        return []

    def sum(self) -> float:
        """returns the max size of the list"""
        return sum(self.get())

    def get_max_size(self) -> int:
        return self._max_size

    def set_max_size(self, new_max_size: int) -> None:
        """sets a new max size"""
        current_list = self.get()
        self._max_size = new_max_size
        self._data = [0] * new_max_size
        self._current_index = -1
        for item in current_list:
            self.append(item)

    def __str__(self) -> str:
        return str(self.get())
