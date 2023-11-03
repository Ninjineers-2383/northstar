from dataclasses import dataclass, field
import numpy
import numpy.typing


@dataclass
class LocalConfig:
    camera_id: int = -1
    device_id: str = ""
    server_ip: str = ""
    stream_port: int = 8000
    has_calibration: bool = False
    camera_matrix: numpy.typing.NDArray[numpy.float64] = field(
        default_factory=lambda: numpy.array([])
    )
    distortion_coefficients: numpy.typing.NDArray[numpy.float64] = field(
        default_factory=lambda: numpy.array([])
    )


@dataclass
class RemoteConfig:
    camera_resolution_width: int = 1280
    camera_resolution_height: int = 720
    camera_auto_exposure: int = 3
    camera_exposure: int = 0
    camera_gain: int = 0
    fiducial_size_m: float = 0.1524
    tag_layout: any = None


@dataclass
class ConfigStore:
    local_config: LocalConfig
    remote_config: RemoteConfig
