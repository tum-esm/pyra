# author            : Patrick Aigner
# email             : patrick.aigner@tum.de
# date              : 20220401
# version           : 3.0
# notes             :
# license           : -
# py version        : 3.10
# ==============================================================================
# description       :
# ==============================================================================

import logging

logger = logging.getLogger("pyra.core")


class EnclosureControl:
    def __init__(self):
        self._SETUP = {}
        self._PARAMS = {}
        self.plc = c.Client()
        self.connection = self.plc_connect()

    def run(self):
        if not self._SETUP["enclosure_presence"]:
            return

        # check what resetbutton after rain does (and the auto reset option)
        # trigger sync with cover if automation is 1

        logger.info("Running EnclosureControl")
        pass

    @property
    def set_config(self):
        pass

    @set_config.setter
    def set_config(self, vals):
        self._SETUP, self._PARAMS = vals

    def plc_connect(self):
        self.plc.connect('10.10.0.4', 0, 1)
        if self.plc.get_connected():
            return True
        else:
            return False

    def plc_disconnect(self):
        logger.debug("plc_disconnect()")
        self.plc.disconnect()

    def reset(self):
        # reset Failure
        logger.debug("reset()")
        msg = self.plc.db_read(3, 4, 1)
        util.set_bool(msg, 0, 5, True)
        self.plc.db_write(3, 4, msg)

    def move_cover(self, angle):
        logger.debug("move_cover()")
        msg = bytearray(2)
        util.set_int(msg, 0, angle)
        self.plc.db_write(6, 8, msg)

    def close_cover(self):  #
        logger.debug("close_cover()")
        self.sync_to_tracker(False)
        self.set_manual_control(True)
        msg = bytearray(2)
        util.set_int(msg, 0, 0)
        self.plc.db_write(6, 8, msg)

    def sync_to_tracker(self, state):   #
        logger.debug("sync_to_tracker()")
        # AngleTrackerOn
        msg = self.plc.db_read(8, 8, 1)
        util.set_bool(msg, 0, 1, state) # was 0
        self.plc.db_write(8, 8, msg)

    def set_manual_control(self, state):    #
        logger.debug("set_manual_control()")
        # ManualControlWeb
        msg = self.plc.db_read(8, 24, 1)
        util.set_bool(msg, 0, 1, state) # was 0
        self.plc.db_write(8, 24, msg)

    def set_fan_speed(self, speed): #
        logger.debug("Set Fanspeed: %s " % speed)
        msg = self.plc.db_read(8, 10, 2) # was 10
        util.set_int(msg, 0, speed)
        self.plc.db_write(8, 10, msg) # was 10 , 22
        temp = self.get_fan_speed()
        #logger.debug("Set/ Get Fanspeed = %s/%s" % (speed,temp))

    def get_fan_speed(self):    #
        msg = self.plc.db_read(8, 10, 2) # was 10 , 22, 4
        speed = util.get_int(msg, 0)
        logger.debug("Get Fan Speed: %s" % speed)
        return speed

    def set_manual_temp(self, state):   #
        logger.debug("Manual Temperature: %s" % state)
        msg = self.plc.db_read(8, 24, 1)
        util.set_bool(msg, 0, 4, state)
        self.plc.db_write(8, 24, msg)

    def get_man_temp_mode(self):    #
        #logger.debug("Get Man Temp Mode: ")
        # DB8, 14.0: Spectrometer
        msg = self.plc.db_read(8, 24, 1)
        state = util.get_bool(msg, 0, 4)
        logger.debug("Get Man Temp Mode: %s " % state)
        return state

    def set_auto_temp(self, state):
        logger.debug("Set Auto Temperature: %s " % state)
        msg = self.plc.db_read(8, 24, 1) # was 18 , 24
        util.set_bool(msg, 0, 5, state) # was 0 , 5
        self.plc.db_write(8, 24, msg)

    def get_auto_temp_mode(self):    #
        #logger.debug("Get Auto Temp Mode: ")
        # DB8, 14.0: Spectrometer
        msg = self.plc.db_read(8, 24, 1) # was 18
        state = util.get_bool(msg, 0, 5) # was 0
        logger.debug("Get Temp Mode: %s " % state)
        return state

    def get_nominal_angle(self):    #
        logger.debug("get_nominal_angle()")
        msg = self.plc.db_read(6, 8, 2)
        angle = util.get_int(msg, 0)
        return angle

    def get_current_angle(self):    #
        logger.debug("get_current_angle()")
        msg = self.plc.db_read(6, 14, 2)
        angle = util.get_int(msg, 0)
        return angle

    def power_spec(self, state):    #
        logger.debug("power_spec()")
        msg = self.plc.db_read(8, 8, 1)
        if state:
            util.set_bool(msg, 0, 2, True)
        else:
            util.set_bool(msg, 0, 2, False)
        self.plc.db_write(8, 8, msg)

    def get_spectrometer_state(self):   #
        logger.debug("get_spectrometer_state()")
        # DB8, 14.0: Spectrometer
        msg = self.plc.db_read(8, 8, 1)
        state = util.get_bool(msg, 0, 2)
        return state

    def power_cam(self, state): #
        logger.debug("power_cam()")
        msg = self.plc.db_read(8, 8, 1)
        if state:
            util.set_bool(msg, 0, 4, True)
        else:
            util.set_bool(msg, 0, 4, False)
        self.plc.db_write(8, 8, msg)

    def get_cam_state(self):    #
        logger.debug("get_cam_state()")
        # DB8, 14.6 EM27Camera
        msg = self.plc.db_read(8, 8, 1)
        state = util.get_bool(msg, 0, 4)
        return state

    def power_heater(self, state):
        logger.debug("Power Heater: %s" % state)
        msg = self.plc.db_read(8, 12, 1)
        if state:
            util.set_bool(msg, 0, 7, True)
        else:
            util.set_bool(msg, 0, 7, False)
        self.plc.db_write(8, 12, msg)

    def get_heater_state(self):
        #logger.debug("Get Heater State: %s" % state)
        msg = self.plc.db_read(8, 12, 1)
        state = util.get_bool(msg, 0, 7)
        logger.debug("Get Heater State: %s\n" % state)
        return state

    def get_NWCheck_state(self):
        logger.debug("get_nwcheck_state()")
        # DB8, 14.6 EM27Camera
        msg = self.plc.db_read(24, 10, 1)
        state = util.get_bool(msg, 0, 3)
        return state

    def check_connection(self, state):
        logger.debug("check_connection()")
        msg = self.plc.db_read(24, 10, 1)
        util.set_bool(msg, 0, 3, state)
        self.plc.db_write(24, 10, msg)

    def power_router(self, state):  #
        logger.debug("power_router()")
        msg = self.plc.db_read(8, 12, 1)
        util.set_bool(msg, 0, 3, state)
        self.plc.db_write(8, 12, msg)

    def power_computer(self, state):    #
        logger.debug("power_computer()")
        msg = self.plc.db_read(8, 13, 1)
        util.set_bool(msg, 0, 0, state)
        self.plc.db_write(8, 13, msg)