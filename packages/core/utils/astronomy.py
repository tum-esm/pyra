import astropy.coordinates as astropy_coordinates
import astropy.time as astropy_time


class Astronomy:
    SETUP = None
    PARAMS = None

    # TODO: Is "elevation" what this should return?
    @staticmethod
    def get_current_sun_elevation():
        """calc_sun_angle_deg(location loc): Computes and returns the current sun
        angle in degree, based on the location loc, computed by get_tracker_position(),
        and current time. Therefore, the pack- ages time and astrophy are required.
        """
        now = astropy_time.Time.now()
        altaz = astropy_coordinates.AltAz(
            location=Astronomy.__get_astropy_location(), obstime=now
        )
        sun = astropy_coordinates.get_sun(now)
        sun_angle_deg = sun.transform_to(altaz).alt
        return sun_angle_deg

    @staticmethod
    def __get_location_from_camtracker_config() -> tuple[float]:
        """Reads the config.txt file of the CamTracker application to receive the
        latest tracker position.

        Returns
        tracker_position as a python list
        """

        # TODO: Coordinates are set inside the camtracker config file. Maybe we can
        # set the camtracker config file based on the config JSONs so that the pyra
        # UI can be used to set the stations coordinates.

        with open(Astronomy.SETUP["camtracker"]["config_path"], "r") as f:
            _lines = f.readlines()

            # find $1 marker
            _marker_line_index = None
            for n, line in enumerate(_lines):
                if line == "$1\n":
                    _marker_line_index = n

            assert _marker_line_index is not None, "Camtracker config file is not valid"

            # (latitude, longitude, altitude)
            return tuple(
                [
                    float(_lines[_marker_line_index + n].replace("\n", ""))
                    for n in [1, 2, 3]
                ]
            )

    @staticmethod
    def __get_astropy_location():
        """
        get_tracker_position(): Reads out the height, the longitude and the
        latitude of the system from CamTrackerConfig.txt, and computes the location
        on earth. Therefore, the python package astropy [23] is imported, and its
        function coord.EarthLocation() is used. The read out parameters, as well as
        the computed location will be returned.
        """
        (
            latitude,
            longitude,
            altitude,
        ) = Astronomy.__get_location_from_camtracker_config()
        return astropy_coordinates.EarthLocation.from_geodetic(
            height=altitude, lat=latitude, lon=longitude
        )
