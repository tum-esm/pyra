# CamTracker is a software that controls two electro motors that are connected
# to mirrors. It tracks the sun movement and allows the spectrometer to follow
# the sun in the course of the day.

# Two methods: 1. Where should the sun be in theory, 2. Use a camera to validate theory. Problematic when clouds appear. When suntracker is confused, then one can use "autostart" to reset the mirror position to the theoretic one.

# TODO: Implement this for the "Camtracker" software
# Later, make an abstract base class that enforces a standard interface
# to be implemented for any software like "Camtracker"

# TODO: Mock the behaviour of OPUS when testing


import logging

logger = logging.getLogger("pyra.core")


class SunTracking:
    @staticmethod
    def run():
        logger.info("Running SunTracking")
        pass
