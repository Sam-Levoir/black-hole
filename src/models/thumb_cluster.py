"""Sam Levoir May 2024"""

from models.moveable import Moveable


class ThumbCluster(Moveable):
    """
    Holds information related to a thumb cluster. This is mostly location information.
    """

    def __init__(
        self, *, key_count: int, arc_inner_radius: float, rotation: tuple[float, float, float], translation: tuple[float, float, float]
    ) -> None:
        super().__init__(rotation=rotation, translation=translation)
        self.key_count = key_count
        self.arc_inner_radius = arc_inner_radius
