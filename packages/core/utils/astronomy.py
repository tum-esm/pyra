from typing import Any, Optional
import os
import skyfield.api
import tum_esm_utils
import datetime
from packages.core import types

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=4)


class Astronomy:
    _PLANETS: Any = None

    @staticmethod
    def load_astronomical_dataset() -> None:
        """Loads the astronomical dataset DE421 from the NASA JPL website,
        see https://ssd.jpl.nasa.gov/planets/eph_export.html."""

        filepath = os.path.join(PROJECT_DIR, "config", "astronomy_dataset_de421.bsp")
        assert os.path.isfile(filepath), "Astronomical dataset not found"

        if Astronomy._PLANETS is None:
            Astronomy._PLANETS = skyfield.api.load_file(filepath)

    @staticmethod
    def get_current_sun_elevation(
        config: types.Config,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        alt: Optional[float] = None,
        datetime_object: Optional[datetime.datetime] = None,
    ) -> float:
        """Computes current sun elevation in degree, based on the
        coordinates from the CamTracker config file."""

        assert Astronomy._PLANETS is not None, "Astronomical dataset not loaded"
        earth = Astronomy._PLANETS["Earth"]
        sun = Astronomy._PLANETS["Sun"]

        if datetime_object is not None:
            current_timestamp = datetime_object.timestamp()  # type: ignore
            assert isinstance(current_timestamp, float)
            current_time = skyfield.api.load.timescale().from_datetime(
                datetime.datetime.fromtimestamp(current_timestamp, tz=skyfield.api.utc)
            )
        else:
            current_time = skyfield.api.load.timescale().now()

        if (lat is None) or (lon is None) or (alt is None):
            lat, lon, alt = Astronomy.get_camtracker_coordinates(config)

        current_position = earth + skyfield.api.wgs84.latlon(
            latitude_degrees=lat,
            longitude_degrees=lon,
            elevation_m=alt,
        )

        sun_pos = current_position.at(current_time).observe(sun).apparent()
        altitude, _, _ = sun_pos.altaz()
        return round(float(altitude.degrees), 3)

    @staticmethod
    def get_camtracker_coordinates(config: types.Config) -> tuple[float, float, float]:
        """Returns the coordinates from the CamTracker config file as (lat, lon, alt)."""

        if config.general.test_mode:
            return (48.151, 11.569, 539)  # TUM_I location in munich

        try:
            with open(config.camtracker.config_path.root, "r") as f:
                _lines = f.readlines()
            _marker_line_index: Optional[int] = None
            for n, line in enumerate(_lines):
                if line == "$1\n":
                    _marker_line_index = n
            assert _marker_line_index is not None, "Could not find $1 marker"
            lat = float(_lines[_marker_line_index + 1].strip())
            lon = float(_lines[_marker_line_index + 2].strip())
            alt = float(_lines[_marker_line_index + 3].strip()) * 1000
            return lat, lon, alt
        except Exception as e:
            raise Exception(
                "Could not read CamTracker config file. Please make sure that "
                f"the config located at {config.camtracker.config_path.root} is "
                "valid or change the path in the config."
            ) from e
