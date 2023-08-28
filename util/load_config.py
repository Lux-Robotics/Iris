import json
import numpy as np


def load_model(filename):
    # Open the JSON file
    # with open(filename) as f:
    #     data = json.load(f)
    #
    # intrinsics = data['intrinsics']
    # intrinsics = [736.778251, 737.4428753, 633.3229938, 405.0528428, 0.01447377326, 0.4859143223, 0.001139373855, -0.001747505697, 0.4118361855, -0.08130091421, 0.5609146927, 0.4840040021]
    intrinsics = [907.9999689, 911.6615495, 777.9274486, 622.7734195, -0.01632715724, 0.02410289232, 0.0009172562383, -0.000259327844, 0.158217454, -0.05968226571, 0.08854174568, 0.1483834672]
    # Create camera matrix
    cameraMatrix = np.array([[intrinsics[0], 0, intrinsics[2]],
                             [0, intrinsics[1], intrinsics[3]],
                             [0, 0, 1]])

    # Distortion coefficient vector
    distCoeffs = np.array(intrinsics[4:])
    print(cameraMatrix)
    print(distCoeffs)

    return cameraMatrix, distCoeffs

camera_matrix, dist_coeffs = load_model("")
# Development in progress
# camera_matrix = np.array([
#     [
#         714.4774572094963,
#         0,
#         619.9129445218975
#     ],
#     [
#         0,
#         715.2506130613575,
#         335.1623849163054
#     ],
#     [
#         0,
#         0,
#         1
#     ]
# ])
# dist_coeffs = np.array([0.05852700572055598,
#         -0.1265085795052399,
#         0.00035059666819713494,
#         -0.00013150863159782646,
#         0.09572578781769861])

apriltag_size = 0.1524  # meters
