from dataclasses import dataclass
from typing import List, Union

import numpy
import numpy.typing
from wpimath.geometry import Pose3d


@dataclass(frozen=True)
class FiducialImageObservation:
    tag_id: int
    corners: numpy.typing.NDArray[numpy.float64]


@dataclass(frozen=True)
class PoseObservation:
    tag_ids: List[int]
    multitag: bool
    pose_0: Pose3d
    error_0: float
    pose_1: Union[Pose3d, None]
    error_1: Union[float, None]


@dataclass(frozen=True)
class FiducialPoseObservation(PoseObservation):
    pass


@dataclass(frozen=True)
class CameraPoseObservation(PoseObservation):
    pass
