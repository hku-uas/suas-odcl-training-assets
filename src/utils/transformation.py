import numpy as np


def rotate(coordinates, angle_degrees):
    angle_radians = np.radians(angle_degrees)
    rotation_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                                [np.sin(angle_radians), np.cos(angle_radians)]])
    return np.dot(coordinates, rotation_matrix)


def scale(coordinates, scale_factors):
    scaling_matrix = np.diag(scale_factors)
    return np.dot(coordinates, scaling_matrix)


def translate(coordinates, translation_vector):
    return coordinates + np.array(translation_vector)


def transform_coords(coordinates, angle_degrees, scale_factor, translation_vector):
    rotated = rotate(coordinates, angle_degrees)
    scaled = scale(rotated, [scale_factor, scale_factor])
    translated = translate(scaled, translation_vector)
    return translated
