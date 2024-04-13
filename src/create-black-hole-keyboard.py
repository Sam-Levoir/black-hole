"""
Generates a "Black Hole" keyboard OpenSCAD file.
The created file should opened in OpenSCAD, rendered, exported as an STL and then 3D printed.

See repo for more information: https://github.com/Sam-Levoir/black-hole

All units are in mm and degrees as that is just how openSCAD does things.

Created by Sam Levoir - April 2024
"""

import math
import os
from solid import OpenSCADObject as shape, cube, translate, scad_render_to_file, rotate, square, rotate_extrude

# region Configurable Constants:
radius_for_key_hole_curvature = 50
angle_between_key_holes = 15
# endregion Configurable Constants

# region Constants Which Should Probably Be Left Alone:
segments = 180  # How round things are. Could be messed with, but no real need for it. This is a balance of round and renderable.
plate_height = 1.5  # Has to be 1.5mm for switches to snap in. Do not change! https://matt3o.com/anatomy-of-a-keyboard/.
key_hole_inner_width = 13.6  # 13.6mm is best by test. I tried a range from 13 - 15. The default is 14: https://matt3o.com/anatomy-of-a-keyboard/.
key_hole_rim_thickness = 3  # Should be just enough to hold the switch and no more.
# endregion Constants Which Should Probably Be Left Alone

# region Calculated Constants:
key_hole_outer_width = key_hole_inner_width + (2 * key_hole_rim_thickness)  # 1 rim thickness on each side of the hole.
# endregion CCalculated Constants


def main():
    black_hole_keyboard: shape = make_plate_strip(3)

    # https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
    this_files_dir = os.path.dirname(os.path.realpath(__file__))
    output_file_path = os.path.join(this_files_dir, "..", "things", "black-hole.scad")
    scad_render_to_file(black_hole_keyboard, output_file_path)


def make_plate_strip(key_count: int) -> shape:
    # Make a keyhole, translate and rotate it into position.
    # Make another keyhole, join it to existing keyhole(s), translate and rotate whole thing into position.
    # Rinse repeat.
    plate_strip: shape | None = None
    for _ in range(key_count):
        key_hole = make_key_hole()

        if plate_strip:
            # There is an existing plate strip (of aggregated key holes) to add onto.
            # First, make a curved strip to join this new key hole to the existing ones.
            plate_face = square((plate_height, key_hole_outer_width))
            plate_face = translate((radius_for_key_hole_curvature - plate_height, 0, 0))(plate_face)
            joining_strip = rotate_extrude(angle_between_key_holes, segments=segments)(plate_face)
            joining_strip = translate((-(radius_for_key_hole_curvature), 0, 0))(joining_strip)
            joining_strip = rotate((0, 90, 0))(joining_strip)
            joining_strip = translate((0, key_hole_outer_width, 0))(joining_strip)

            # Now, rotate the existing key holes and move them over into place.
            plate_strip = rotate((angle_between_key_holes, 0, 0))(plate_strip)

            # Then move it over.
            y_translation_distance_for_rotation = radius_for_key_hole_curvature * sin(angle_between_key_holes)
            z_translation_distance_for_rotation = radius_for_key_hole_curvature - math.sqrt(
                math.pow(radius_for_key_hole_curvature, 2) - math.pow(y_translation_distance_for_rotation, 2)
            )
            y_translation_distance = key_hole_outer_width + y_translation_distance_for_rotation
            plate_strip = translate((0, y_translation_distance, z_translation_distance_for_rotation))(plate_strip)

            # Now put everything together!
            plate_strip += joining_strip
            plate_strip += key_hole
        else:
            # There is no existing plate strip, then this key hole is the start of the plate strip!
            plate_strip = key_hole

    # This will only ever be None if someone passes a key_count of 0. Garbage in, garbage out.
    return plate_strip  # type: ignore


def make_key_hole() -> shape:
    outer_cube = cube([key_hole_outer_width, key_hole_outer_width, plate_height])
    inner_cube = cube([key_hole_inner_width, key_hole_inner_width, plate_height])

    # We need to translate the inner cube so that it is centered inside of the outer cube.
    # Translate it by the thickness of the rim in both the x and y directions to put it in the center.
    inner_cube = translate((key_hole_rim_thickness, key_hole_rim_thickness, 0))(inner_cube)

    # Then just cut the inner cube out of the outer, and we have a keyhole!
    key_hole = outer_cube - inner_cube
    return key_hole


def cos(angle_in_degrees: float):
    return math.cos(math.radians(angle_in_degrees))


def sin(angle_in_degrees: float):
    return math.sin(math.radians(angle_in_degrees))


def tan(angle_in_degrees: float):
    return math.tan(math.radians(angle_in_degrees))


if __name__ == "__main__":
    main()