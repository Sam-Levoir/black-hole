"""
Generates a "Black Hole" keyboard OpenSCAD file.
The created file should opened in OpenSCAD, rendered, exported as an STL and then 3D printed.

See repo for more information: https://github.com/Sam-Levoir/black-hole

All units are in mm and degrees as that is just how openSCAD does things.

Created by Sam Levoir - April 2024
"""

import math
import os
from solid import OpenSCADObject as Shape, cube, translate, scad_render_to_file, rotate, square, rotate_extrude

from models.column import Column
from models.thumb_cluster import ThumbCluster

# region Configurable Constants:
pointer_finger_column = Column(key_count=3, angle_between_key_holes=10, radius_for_key_hole_curvature=10, rotation=(0, 10, 5), translation=(0, 0, 20))
middle_finger_column = Column(key_count=3, angle_between_key_holes=10, radius_for_key_hole_curvature=10, rotation=(0, 10, 0), translation=(25, 0, 15))
ring_finger_column = Column(key_count=3, angle_between_key_holes=10, radius_for_key_hole_curvature=10, rotation=(0, 10, -4), translation=(50, 0, 10))
pinky_finger_column = Column(key_count=3, angle_between_key_holes=10, radius_for_key_hole_curvature=10, rotation=(0, 10, -8), translation=(75, 0, 5))

thumb_cluster = ThumbCluster(key_count=3, arc_inner_radius=100, rotation=(0, 0, 130), translation=(-15, -10, 0))
# endregion Configurable Constants

# region Constants Which Should Probably Be Left Alone:
segments = 180  # How round things are. Could be messed with, but no real need for it. This is a balance of round and renderable.
plate_height = 1.5  # Has to be 1.5mm for switches to snap in. Do not change! https://matt3o.com/anatomy-of-a-keyboard/.
key_hole_inner_width = 13.6  # 13.6mm is best by test. I tried a range from 13 - 15. The default is 14: https://matt3o.com/anatomy-of-a-keyboard/.
key_hole_rim_thickness = 3  # Should be just enough to hold the switch and no more.
radial_padding_between_thumb_cluster_keys = 0  # Adjusts how close the thumb keys are to each other.
# endregion Constants Which Should Probably Be Left Alone

# region Calculated Constants:
columns = [pointer_finger_column, middle_finger_column, ring_finger_column, pinky_finger_column]
key_hole_outer_width = key_hole_inner_width + (2 * key_hole_rim_thickness)  # 1 rim thickness on each side of the hole.
# endregion CCalculated Constants


def main():
    half: Shape = make_half()

    # https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
    this_files_dir = os.path.dirname(os.path.realpath(__file__))
    output_file_path = os.path.join(this_files_dir, "..", "things", "black-hole.scad")
    scad_render_to_file(half, output_file_path)


def make_half() -> Shape:
    half: Shape | None = None
    for column in columns:
        plate_strip = make_plate_strip(column)
        plate_strip = rotate(column.rotation)(plate_strip)
        plate_strip = translate(column.translation)(plate_strip)

        if half is None:
            half = plate_strip
        else:
            half += plate_strip

    thumb_plate_arc = make_thumb_plate_arc(thumb_cluster)
    thumb_plate_arc = rotate(thumb_cluster.rotation)(thumb_plate_arc)
    thumb_plate_arc = translate(thumb_cluster.translation)(thumb_plate_arc)

    # This will only ever be None if there are no columns defined, which ruins the whole point of a keyboard anyways.
    half += thumb_plate_arc  # type: ignore

    # Add a floor for 3d printing, so everything stays in relative positions.
    floor_height = 1
    floor = cube([180, 130, floor_height], center=True)
    floor = translate((20, 2, 0))(floor)
    half = translate((0, 0, floor_height))(half)  # type: ignore
    half += floor

    return half  # type: ignore


def make_plate_strip(column: Column) -> Shape:
    # Make a keyhole, translate and rotate it into position.
    # Make another keyhole, join it to existing keyhole(s), translate and rotate whole thing into position.
    # Rinse repeat.
    plate_strip: Shape | None = None
    for _ in range(column.key_count):
        key_hole = make_key_hole()

        if plate_strip:
            radius_for_key_hole_curvature = column.radius_for_key_hole_curvature
            angle_between_key_holes = column.angle_between_key_holes

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


def make_thumb_plate_arc(thumb_cluster: ThumbCluster) -> Shape:
    arc_inner_radius = thumb_cluster.arc_inner_radius
    arc_depth = key_hole_outer_width
    arc_center_radius = arc_inner_radius + (arc_depth / 2)

    # Make a key hole, rotate the arc, make another, tack them all together.
    thumb_plate_arc: Shape | None = None
    for _ in range(thumb_cluster.key_count):
        # Make the arc for this key hole.
        plate_face = square((arc_depth, plate_height))
        plate_face = translate((arc_inner_radius, 0, 0))(plate_face)

        key_hole_inner_arc_length = key_hole_outer_width + radial_padding_between_thumb_cluster_keys
        angle_between_thumb_holes = (180 * key_hole_inner_arc_length) / (math.pi * arc_inner_radius)

        thumb_plate_arc_segment = rotate_extrude(angle_between_thumb_holes, segments=segments)(plate_face)

        # Punch the key hole in the arc.
        key_hole_cube = cube([key_hole_inner_width, key_hole_inner_width, plate_height], center=True)
        # Translate and rotate it into position. It is centered on z axis too, so we have to translate it back up a little.
        key_hole_cube = translate((arc_center_radius, 0, plate_height / 2))(key_hole_cube)
        key_hole_cube = rotate((angle_between_thumb_holes / 2))(key_hole_cube)

        finished_key_hole_arc_segment = thumb_plate_arc_segment - key_hole_cube

        # Tack this finished segment on to the rest of the thumb plate arc.
        if thumb_plate_arc is None:
            thumb_plate_arc = finished_key_hole_arc_segment
        else:
            thumb_plate_arc = rotate(angle_between_thumb_holes)(thumb_plate_arc)
            thumb_plate_arc += finished_key_hole_arc_segment

    # This will only ever be None if someone passes a key_count of 0. Garbage in, garbage out.
    # Move the whole thing back to 0,0,0 so the calling function can have an easier time moving it around.
    thumb_plate_arc = translate((-arc_inner_radius, 0, 0))(thumb_plate_arc)  # type: ignore
    return thumb_plate_arc  # type: ignore


def make_key_hole() -> Shape:
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
