"""Sam Levoir May 2024"""


class Moveable:
    """
    Represents an object which can be moved. More of an abstract class.
    """

    def __init__(self, *, rotation: tuple[float, float, float], translation: tuple[float, float, float]) -> None:
        self.rotation = rotation
        self.translation = translation
