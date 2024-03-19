from typing import List, Union

import cv2
import numpy
from config.config import ConfigStore
from vision_types import (
    FiducialImageObservation,
    PoseObservation,
)
from wpimath.geometry import Pose3d, Rotation3d, Quaternion, Translation3d, Transform3d

from pipeline.coordinate_systems import openCvPoseToWpilib, wpilibTranslationToOpenCv
from pipeline.FiducialPoseEstimator import (
    SquareTargetPoseEstimator,
)


class CameraPoseEstimator:
    def __init__(self) -> None:
        raise NotImplementedError

    def solve_camera_pose(
        self,
        image_observations: List[FiducialImageObservation],
        config_store: ConfigStore,
    ) -> Union[PoseObservation, None]:
        raise NotImplementedError


class MultiTargetCameraPoseEstimator(CameraPoseEstimator):
    fallback_estimator: SquareTargetPoseEstimator = None

    def __init__(self) -> None:
        self.fallback_estimator: SquareTargetPoseEstimator = SquareTargetPoseEstimator()

    def solve_camera_pose(
        self,
        image_observations: List[FiducialImageObservation],
        config_store: ConfigStore,
    ) -> Union[List[PoseObservation], None]:
        # If only one tag or no tag layout
        if (
            len(image_observations) == 1
            or config_store.remote_config.tag_layout is None
        ):
            print(f"Fallback to single pose with {len(image_observations)} observations and {config_store.remote_config.tag_layout}")
            return [
                self.fallback_estimator.solve_fiducial_pose(observation, config_store)
                for observation in image_observations
            ]

        # Exit if no observations available
        if len(image_observations) == 0:
            return None

        # Create set of object and image points
        fid_size = config_store.remote_config.fiducial_size_m
        object_points = []
        image_points = []
        tag_ids = []
        tag_poses = []
        for observation in image_observations:
            tag_pose = None
            for tag_data in config_store.remote_config.tag_layout["tags"]:
                if tag_data["ID"] == observation.tag_id:
                    tag_pose = Pose3d(
                        Translation3d(
                            tag_data["pose"]["translation"]["x"],
                            tag_data["pose"]["translation"]["y"],
                            tag_data["pose"]["translation"]["z"],
                        ),
                        Rotation3d(
                            Quaternion(
                                tag_data["pose"]["rotation"]["quaternion"]["W"],
                                tag_data["pose"]["rotation"]["quaternion"]["X"],
                                tag_data["pose"]["rotation"]["quaternion"]["Y"],
                                tag_data["pose"]["rotation"]["quaternion"]["Z"],
                            )
                        ),
                    )
            if tag_pose is not None:
                # Add object points by transforming from the tag center
                corner_0 = tag_pose + Transform3d(
                    Translation3d(0, fid_size / 2.0, -fid_size / 2.0), Rotation3d()
                )
                corner_1 = tag_pose + Transform3d(
                    Translation3d(0, -fid_size / 2.0, -fid_size / 2.0), Rotation3d()
                )
                corner_2 = tag_pose + Transform3d(
                    Translation3d(0, -fid_size / 2.0, fid_size / 2.0), Rotation3d()
                )
                corner_3 = tag_pose + Transform3d(
                    Translation3d(0, fid_size / 2.0, fid_size / 2.0), Rotation3d()
                )
                object_points += [
                    wpilibTranslationToOpenCv(corner_0.translation()),
                    wpilibTranslationToOpenCv(corner_1.translation()),
                    wpilibTranslationToOpenCv(corner_2.translation()),
                    wpilibTranslationToOpenCv(corner_3.translation()),
                ]

                # Add image points from observation
                image_points += [
                    [observation.corners[0][0][0], observation.corners[0][0][1]],
                    [observation.corners[0][1][0], observation.corners[0][1][1]],
                    [observation.corners[0][2][0], observation.corners[0][2][1]],
                    [observation.corners[0][3][0], observation.corners[0][3][1]],
                ]

                # Add tag ID and pose
                tag_ids.append(observation.tag_id)
                tag_poses.append(tag_pose)

        # Single tag, raise exception
        if len(tag_ids) == 1:
            # raise Exception(
            #     "Only one tag in layout, make sure all tags are in the layout"
            # )
            print("Fallback to single pose estimation with one recognized tag id")
            return [
                self.fallback_estimator.solve_fiducial_pose(observation, config_store)
                for observation in image_observations
            ]

        # Multi-tag, return one pose
        else:
            # Run SolvePNP with all tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    numpy.array(object_points),
                    numpy.array(image_points),
                    config_store.local_config.camera_matrix,
                    config_store.local_config.distortion_coefficients,
                    flags=cv2.SOLVEPNP_SQPNP,
                )
            except Exception as e:
                print(e)
                return None

            # Calculate WPILib camera pose
            camera_to_field_pose = openCvPoseToWpilib(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(
                camera_to_field_pose.translation(), camera_to_field_pose.rotation()
            )
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(
                field_to_camera.translation(), field_to_camera.rotation()
            )

            # Return result
            return [
                PoseObservation(
                    tag_ids, True, field_to_camera_pose, errors[0][0], None, None
                )
            ]
