from scipy.spatial import ConvexHull
import itertools
import numpy as np


def area_of_quadrilateral(points):
    # Assume points are in the correct order to form a quadrilateral
    # and calculate the area using the shoelace formula
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    area = abs(area) / 2.0
    return area


def find_max_area_quadrilateral(coordinates):
    # Find the convex hull
    hull = ConvexHull(coordinates)
    hull_points = coordinates[hull.vertices]

    max_area = 0
    best_combination = None

    # Iterate through all combinations of four points on the convex hull
    for indices in itertools.combinations(range(len(hull_points)), 4):
        quad_coords = hull_points[list(indices)]
        area = area_of_quadrilateral(quad_coords)
        if area > max_area:
            max_area = area
            best_combination = indices

    # Map the indices from the hull points back to the original coordinates
    best_indices = [hull.vertices[i] for i in best_combination]

    return best_indices
