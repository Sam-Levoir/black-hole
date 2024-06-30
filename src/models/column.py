"""Sam Levoir April 2024"""

from models.moveable import Moveable


class Column(Moveable):
    """
    Holds information related to a column of keys, for example the three keys which your pinky touch are the "pinky column".
    This is mostly location information.
    """

    def __init__(
        self,
        *,
        key_count: int,
        radius_for_key_hole_curvature: float,
        angle_between_key_holes: float,
        rotation: tuple[float, float, float],
        translation: tuple[float, float, float]
    ) -> None:
        super().__init__(rotation=rotation, translation=translation)
        self.key_count = key_count
        self.radius_for_key_hole_curvature = radius_for_key_hole_curvature
        self.angle_between_key_holes = angle_between_key_holes
