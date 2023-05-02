from typing import Any, Optional
import astropy.coordinates as astropy_coordinates
import astropy.time as astropy_time
import astropy.units as astropy_units
from packages.core import types


# TODO: replace this with a better library


class Astronomy:
    """Provides a method to compute the current sun elevation
    based on the coordinates from the CamTracker config file."""

    CONFIG: Optional[types.ConfigDict] = None
    units = astropy_units

    @staticmethod
    def get_current_sun_elevation() -> Any:
        """Computes current sun elevation in degree, based on the
        coordinates from the CamTracker config file."""

        assert Astronomy.CONFIG is not None, "astronomy has no config yet"

        with open(Astronomy.CONFIG["camtracker"]["config_path"], "r") as f:
            _lines = f.readlines()

        # find $1 marker
        _marker_line_index = None
        for n, line in enumerate(_lines):
            if line == "$1\n":
                _marker_line_index = n

        assert _marker_line_index is not None, "Camtracker config file is not valid"
        lat = float(_lines[_marker_line_index + 1].strip())
        lon = float(_lines[_marker_line_index + 2].strip())
        alt = float(_lines[_marker_line_index + 3].strip())

        now = astropy_time.Time.now()

        altaz = astropy_coordinates.AltAz(
            location=astropy_coordinates.EarthLocation.from_geodetic(
                height=alt, lat=lat, lon=lon
            ),
            obstime=now,
        )
        sun = astropy_coordinates.get_sun(now)
        sun_angle_deg = sun.transform_to(altaz).alt
        return sun_angle_deg
