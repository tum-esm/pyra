import datetime
import os
import threading
import time
from typing import Any, Optional

import numpy as np
import psutil
import tum_esm_utils
from tum_esm_utils.opus import OpusHTTPInterface

from packages.core import interfaces, types, utils

from .abstract_thread import AbstractThread


class OpusProgram:
    """Class for starting and stopping OPUS."""

    @staticmethod
    def start(config: types.Config, logger: utils.Logger) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        with interfaces.StateInterface.update_state(logger) as s:
            s.activity.opus_startups += 1

        logger.info("Starting OPUS")
        os.startfile(  # type: ignore
            os.path.basename(config.opus.executable_path.root),
            cwd=os.path.dirname(config.opus.executable_path.root),
            arguments=f"/HTTPSERVER=ON /LANGUAGE=ENGLISH /DIRECTLOGINPASSWORD={config.opus.username}@{config.opus.password}",
            show_cmd=2,
        )
        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: OpusProgram.is_running(logger),
            timeout_message="OPUS.exe did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=5,
        )
        try:
            tum_esm_utils.timing.wait_for_condition(
                is_successful=OpusHTTPInterface.is_working,
                timeout_message="OPUS HTTP interface did not start within 90 seconds.",
                timeout_seconds=90,
                check_interval_seconds=5,
            )
        except TimeoutError as e:
            raise ConnectionError("OPUS HTTP interface did not start within 90 seconds.") from e

        logger.info("Successfully started OPUS")
        time.sleep(3)

    @staticmethod
    def is_running(logger: utils.Logger) -> bool:
        """Checks if OPUS is already running by searching for processes with
        the executable `opus.exe` or `OpusCore.exe`."""

        logger.debug("Checking if OPUS is running")
        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    return True
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess, IndexError):
                pass

        return False

    @staticmethod
    def stop(logger: utils.Logger) -> None:
        """Closes OPUS. First via the HTTP interface, then forcefully by killing the process."""

        try:
            logger.info("Trying to stop OPUS gracefully via HTTP interface")
            OpusHTTPInterface.unload_all_files()
            logger.info("Successfully unloaded all files")
            time.sleep(1)
            OpusHTTPInterface.close_opus()

            logger.info("Waiting for OPUS to close gracefully")
            try:
                tum_esm_utils.timing.wait_for_condition(
                    is_successful=lambda: not OpusProgram.is_running(logger),
                    timeout_message="OPUS.exe did not stop within 60 seconds.",
                    timeout_seconds=60,
                    check_interval_seconds=4,
                )
                logger.info("Successfully stopped OPUS")
                return
            except TimeoutError:
                logger.warning("OPUS.exe did not stop gracefully within 60 seconds.")
        except Exception as e:
            logger.exception(e)
            logger.error("Could not stop OPUS gracefully via HTTP interface")

        logger.info("Force killing OPUS")
        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    p.kill()
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass
        logger.info("Successfully force killed OPUS")


class OpusThread(AbstractThread):
    """Thread for controlling OPUS.

    * starts/stops the OPUS executable whenever it is not running and `config.general.min_sun_elevation` is reached
    * starts/stops the macro whenever measurements should be running
    * raises an exception if the macro crashes unexpectedly
    * on startup, detects if OPUS is already running an unidentified macro - if so, stops OPUS entirely
    * stores the macro ID so if Pyra Core or this thread crashes, it can continue using the same macro thread
    * Pings the EM27 every 5 minutes to check if it is still connected
    """

    logger_origin = "opus-thread"
    peak_position_cache: dict[str, tuple[int, int]] = {}

    @staticmethod
    def should_be_running(
        config: types.Config,
        logger: utils.Logger,
    ) -> bool:
        """Based on the config, should the thread be running or not?"""
        return True

    @staticmethod
    def get_new_thread_object(
        state_lock: threading.Lock,
        logs_lock: threading.Lock,
    ) -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(
            target=OpusThread.main,
            daemon=True,
            args=(state_lock, logs_lock),
        )

    @staticmethod
    def main(
        state_lock: threading.Lock,
        logs_lock: threading.Lock,
        headless: bool = False,
    ) -> None:
        logger = utils.Logger(origin="opus", lock=logs_lock)
        logger.info("Starting OPUS thread")

        current_experiment: Optional[str] = None  # filepath
        current_macro: Optional[tuple[int, str]] = None  # id and filepath

        logger.debug("Loading configuration file")
        config = types.Config.load()

        logger.debug("Loading state file")
        state = interfaces.StateInterface.load_state(logger)

        thread_start_time = time.time()
        last_successful_ping_time = time.time()
        last_peak_positioning_time: Optional[float] = None
        last_http_connection_issue_time: Optional[float] = None

        try:
            # CHECK IF OPUS IS ALREADY RUNNING
            # ONLY RESTART IF THERE IS AN UNIDENTIFIED MACRO RUNNING
            if OpusProgram.is_running(logger) and (not config.general.test_mode):
                logger.info("OPUS is already running")

                if not OpusHTTPInterface.is_working():
                    logger.warning("OPUS HTTP interface is not working, stopping OPUS")
                    OpusProgram.stop(logger)
                else:
                    logger.info("OPUS HTTP interface is working")
                    current_experiment = OpusHTTPInterface.get_loaded_experiment()

                    if OpusHTTPInterface.some_macro_is_running():
                        logger.info("Some macro is already running")
                        mid = state.opus_state.macro_id
                        mfp = state.opus_state.macro_filepath

                        if (
                            (mid is None)
                            or (mfp is None)
                            or (not OpusHTTPInterface.macro_is_running(mid))
                        ):
                            logger.info("Macro ID is unknown, stopping OPUS entirely")
                            OpusProgram.stop(logger)
                        else:
                            logger.info("The Macro started by Pyra is still running, nothing to do")
                            current_macro = (mid, mfp)

            with interfaces.StateInterface.update_state(logger) as s:
                s.opus_state.experiment_filepath = current_experiment
                s.opus_state.macro_id = None if current_macro is None else current_macro[0]
                s.opus_state.macro_filepath = None if current_macro is None else current_macro[1]
                last_http_connection_issue_time = s.opus_state.last_http_connection_issue_time

            while True:
                t1 = time.time()
                logger.debug("Starting iteration")

                if (thread_start_time - t1) > 43200:
                    # Windows happens to have a problem with long-running multiprocesses/multithreads
                    logger.debug(
                        "Stopping and restarting thread after 12 hours for stability reasons"
                    )
                    return

                logger.debug("Loading configuration file")
                config = types.Config.load()

                opus_should_be_running = (
                    utils.Astronomy.get_current_sun_elevation(config)
                    >= config.general.min_sun_elevation
                )

                if config.general.test_mode:
                    logger.info("OPUS thread is skipped in test mode")
                    logger.debug("Sleeping 15 seconds")
                    time.sleep(15)
                    continue

                # START AND STOP OPUS

                opus_is_running = OpusProgram.is_running(logger)

                if opus_should_be_running and (not opus_is_running):
                    logger.info("OPUS should be running, starting OPUS")
                    OpusProgram.start(config, logger)
                    continue

                if (not opus_should_be_running) and opus_is_running:
                    logger.info("OPUS should not be running, stopping OPUS")
                    if current_macro is None:
                        logger.info("No macro to stop")
                    else:
                        if OpusHTTPInterface.macro_is_running(current_macro[0]):
                            logger.info("Stopping macro")
                            OpusHTTPInterface.stop_macro(current_macro[1])
                            current_macro = None
                            with interfaces.StateInterface.update_state(logger) as s:
                                s.opus_state.macro_id = None
                                s.opus_state.macro_filepath = None

                    OpusProgram.stop(logger)
                    time.sleep(3)
                    continue

                # IDLE AT NIGHT

                if not opus_should_be_running:
                    logger.debug("Sleeping 30 seconds (idling at night)")
                    time.sleep(30)
                    continue

                # LOAD CORRECT EXPERIMENT

                if config.opus.experiment_path.root != current_experiment:
                    if current_experiment is None:
                        logger.info("Loading experiment")
                    else:
                        logger.info("Experiment file has changed, loading new experiment")
                    OpusHTTPInterface.load_experiment(config.opus.experiment_path.root)
                    current_experiment = config.opus.experiment_path.root
                    logger.info(f"Experiment file {current_experiment} was loaded")
                    with interfaces.StateInterface.update_state(logger) as s:
                        s.opus_state.experiment_filepath = current_experiment

                # DETERMINE WHETHER MEASUREMENTS SHOULD BE RUNNING

                state = interfaces.StateInterface.load_state(logger)
                measurements_should_be_running = bool(state.measurements_should_be_running)
                if measurements_should_be_running:
                    # only measure if cover is open
                    if state.tum_enclosure_state.actors.current_angle is not None:
                        measurements_should_be_running = (
                            20 < state.tum_enclosure_state.actors.current_angle < 340
                        )
                        if not measurements_should_be_running:
                            logger.info("Cover is closed, not running any measurements")

                # PING EM27 EVERY 5 MINUTES

                if measurements_should_be_running:
                    if last_successful_ping_time < (time.time() - 300):
                        logger.info("Pinging EM27")
                        tum_esm_utils.timing.wait_for_condition(
                            is_successful=lambda: os.system("ping -n 3 " + config.opus.em27_ip.root)
                            == 0,
                            timeout_seconds=90,
                            timeout_message="EM27 did not respond to ping within 90 seconds.",
                            check_interval_seconds=9,
                        )
                        last_successful_ping_time = time.time()
                        logger.info("Successfully pinged EM27")

                # STARTING MACRO

                if measurements_should_be_running and (current_macro is None):
                    logger.info("Starting macro")

                    macro_successfully_started: bool = False
                    mid = 0  # required for mypy checks to pass
                    for i in range(5):
                        mid = OpusHTTPInterface.start_macro(config.opus.macro_path.root)
                        time.sleep(5)
                        if OpusHTTPInterface.macro_is_running(mid):
                            macro_successfully_started = True
                            break

                    if not macro_successfully_started:
                        raise RuntimeError("Could not start macro within 3 tries")

                    current_macro = (mid, config.opus.macro_path.root)
                    logger.info(f"Successfully started Macro {current_macro[1]}")

                # STOPPING MACRO WHEN MACRO FILE CHANGES OR MEASUREMENTS SHOULD NOT BE RUNNING

                if current_macro is not None:
                    should_stop_macro: bool = False
                    if measurements_should_be_running and (
                        config.opus.macro_path.root != current_macro[1]
                    ):
                        logger.info("Macro file has changed")
                        should_stop_macro = True

                    if not measurements_should_be_running:
                        logger.info("Macro should not be running")
                        should_stop_macro = True

                    if should_stop_macro:
                        OpusHTTPInterface.stop_macro(current_macro[1])
                        current_macro = None
                        logger.info("Successfully stopped Macro")

                # CHECK IF MACRO HAS CRASHED

                if current_macro is not None:
                    if OpusHTTPInterface.macro_is_running(current_macro[0]):
                        logger.debug("Macro is running as expected")
                    else:
                        logger.warning("Macro has stopped/crashed, restarting it")
                        current_macro = None

                # POSSIBLY SET PEAK POSITION

                if config.opus.automatic_peak_positioning and (last_peak_positioning_time is None):
                    if current_macro is not None:
                        last_em27_powerup_time = (
                            interfaces.EM27Interface.get_last_powerup_timestamp(config.opus.em27_ip)
                        )
                        if last_em27_powerup_time is None:
                            logger.info("Could not determine last powerup time of EM27")
                        elif (time.time() - last_em27_powerup_time) < 180:
                            logger.info(
                                "EM27 was powered up less than 3 minutes ago, skipping peak positioning"
                            )
                        else:
                            logger.info("Trying to set peak position")
                            try:
                                OpusThread.set_peak_position(config, logger)
                                last_peak_positioning_time = time.time()
                            except (ValueError, RuntimeError) as e:
                                logger.error(f"Could not set peak position: {e}")

                # DETECT WHEN EM27 HAD A POWER CYCLE SINCE LAST PEAK POSITION CHECK

                if config.opus.automatic_peak_positioning and (
                    last_peak_positioning_time is not None
                ):
                    last_em27_powerup_time = interfaces.EM27Interface.get_last_powerup_timestamp(
                        config.opus.em27_ip
                    )
                    if last_em27_powerup_time is None:
                        logger.info("Could not determine last powerup time of EM27")
                    elif last_peak_positioning_time < (last_em27_powerup_time + 175):
                        logger.info(
                            "EM27 had a power cycle since the last peak positioning, repeating peak positioning in the next loop"
                        )
                        last_peak_positioning_time = None

                # UPDATING STATE

                clear_issues = (time.time() - thread_start_time) >= 180
                if not clear_issues:
                    logger.info(
                        "Waiting for thread to run for 3 minutes before clearing exceptions"
                    )

                with interfaces.StateInterface.update_state(logger) as s:
                    if current_macro is None:
                        s.opus_state.macro_id = None
                        s.opus_state.macro_filepath = None
                    else:
                        s.opus_state.macro_id = current_macro[0]
                        s.opus_state.macro_filepath = current_macro[1]
                    if clear_issues:
                        s.exceptions_state.clear_exception_origin("opus")

                # SLEEP

                t2 = time.time()
                sleep_time = max(5, config.general.seconds_per_core_iteration - (t2 - t1))
                logger.debug(f"Sleeping {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

        except Exception as e:
            logger.exception(e)
            OpusProgram.stop(logger)

            silence_exception: bool = False
            now = time.time()

            # forget about the last http connection issue if it was more than 10 minutes ago
            if last_http_connection_issue_time is not None:
                if (now - last_http_connection_issue_time) > 600:
                    last_http_connection_issue_time = None

            if isinstance(e, ConnectionError):
                if last_http_connection_issue_time is None:
                    silence_exception = True
                    logger.error(
                        "Not sending emails about ConnectionError when it doesn't repeat within 10 minutes"
                    )
                else:
                    logger.error(
                        "ConnectionError repeated within 10 minutes, sending email about it"
                    )
                last_http_connection_issue_time = now

            with interfaces.StateInterface.update_state(logger) as s:
                s.opus_state.macro_id = None
                s.opus_state.macro_filepath = None
                s.opus_state.last_http_connection_issue_time = last_http_connection_issue_time
                if not silence_exception:
                    s.exceptions_state.add_exception(origin="opus", exception=e)
            logger.info("Sleeping 3 minutes until retrying")
            time.sleep(180)
            logger.info("Stopping thread")
            return

    @staticmethod
    def test_setup(
        config: types.Config,
        logger: utils.Logger,
    ) -> None:
        OpusProgram.start(config, logger)

        OpusHTTPInterface.load_experiment(config.opus.experiment_path.root)
        time.sleep(5)

        macro_id = OpusHTTPInterface.start_macro(config.opus.macro_path.root)
        time.sleep(5)
        assert OpusHTTPInterface.macro_is_running(macro_id), "Macro is not running"

        OpusHTTPInterface.stop_macro(config.opus.macro_path.root)
        time.sleep(2)

        tum_esm_utils.timing.wait_for_condition(
            is_successful=lambda: not OpusHTTPInterface.macro_is_running(macro_id),
            timeout_message="Macro did not stop within 60 seconds.",
            timeout_seconds=60,
            check_interval_seconds=4,
        )
        OpusProgram.stop(logger)

    @staticmethod
    def set_peak_position(
        config: types.Config,
        logger: utils.Logger,
    ) -> None:
        """Set the peak position based on the latest OPUS files.

        The function throws a `ValueError` or `RuntimeError` if the peak position cannot be set."""

        # find newest three readable OPUS files
        today = datetime.date.today()
        ifg_file_directory = (
            config.opus.interferogram_path.replace("%Y", f"{today.year:04d}")
            .replace("%y", f"{today.year % 100:02d}")
            .replace("%m", f"{today.month:02d}")
            .replace("%d", f"{today.day:02d}")
        )
        if not os.path.exists(ifg_file_directory):
            raise ValueError(f"Directory {ifg_file_directory} does not exist")

        # Only consider files created within the last 10 minutes
        # and at least 1 minute after the last powerup of the EM27
        last_em27_powerup_time = interfaces.EM27Interface.get_last_powerup_timestamp(
            config.opus.em27_ip
        )
        if last_em27_powerup_time is None:
            raise RuntimeError("Could not determine last powerup time of EM27")
        time_since_powerup = time.time() - last_em27_powerup_time
        logger.debug(f"APP: Time since last powerup is {time_since_powerup:.2f} seconds")

        # I don't use this interface to read ABP anymore, because sometime it is set to -1
        # current_peak_position = interfaces.EM27Interface.get_peak_position(config.opus.em27_ip)

        # find the most recent files
        most_recent_files = utils.find_most_recent_files(
            ifg_file_directory,
            time_limit=min(900, time_since_powerup - 60),
            time_indicator="created",
        )
        logger.debug(
            f"APP: Found {len(most_recent_files)} files created since the last powerup and less than 15 minutes old"
        )

        # remove unused cache items
        unused_keys = set(OpusThread.peak_position_cache.keys()) - set(most_recent_files)
        for k in unused_keys:
            del OpusThread.peak_position_cache[k]

        # compute peak position of these files using the first channel
        configured_abps: list[int] = []
        computed_pps: list[int] = []
        for f in most_recent_files:
            if len(computed_pps) == 5:
                break

            cache_result = OpusThread.peak_position_cache.get(f, None)
            if cache_result is not None:
                configured_abps.append(cache_result[0])
                computed_pps.append(cache_result[1])
                continue
            try:
                opus_file = tum_esm_utils.opus.OpusFile.read(f, read_all_channels=False)
                ifg = opus_file.interferogram
                assert ifg is not None

                # use ABP from files rather than from web interface
                abp = opus_file.channel_parameters[0].instrument["ABP"]
                assert isinstance(abp, (float, int)), f"ABP is not a number (got {abp})"

                fwd_pass: np.ndarray[Any, Any] = ifg[0][: ifg.shape[1] // 2]
                assert len(fwd_pass) == 114256, (
                    f"Interferogram has wrong length (got {len(fwd_pass)}, expected 114256)"
                )

                peak = int(np.argmax(np.abs(fwd_pass)))
                ifg_center = fwd_pass.shape[0] // 2
                assert abs(peak - ifg_center) < 200, (
                    f"Peak is too far off (center = {ifg_center}, peak = {peak})"
                )

                dc_amplitude = abs(np.mean(fwd_pass[:100]))
                assert dc_amplitude >= config.opus.automatic_peak_positioning_dcmin, (
                    f"DC amplitude is too low (DC amplitude = {dc_amplitude})"
                )

                logger.debug(
                    f"APP: {f} - Found peak position {peak} (ABP = {abp}, DC amplitude = {dc_amplitude})"
                )
                configured_abps.append(int(abp))
                computed_pps.append(peak)
                OpusThread.peak_position_cache[f] = (int(abp), peak)
            except Exception as e:
                logger.debug(f"APP: {f} - Could not determine peak position ({e})")
        if len(computed_pps) < 5:
            raise ValueError(
                f"Could not determine enough peak positions from interferograms (found {len(computed_pps)}, expected 5)"
            )
        assert len(configured_abps) == 5

        # compare computed peak positions to each other
        if any([p != computed_pps[0] for p in computed_pps[1:]]):
            raise ValueError(f"Peak positions are not identical: {computed_pps}")

        # compare ABP values to each other
        if any([a != configured_abps[0] for a in configured_abps[1:]]):
            raise ValueError(f"ABP values are not identical: {configured_abps}")

        # only use the values if ABP and computed peak stays constant for 5 interferograms
        configured_abp = configured_abps[0]
        computed_pp = computed_pps[0]
        logger.debug(f"APP: Currently configured ABP is {configured_abp}")

        # the computed peak should be directly in the center of the interferogram
        # hence, from the offset the pp has from the center, we can compute the change
        # in ABP that is necessary to center the peak position
        pp_offset_from_center = computed_pp - 57128
        new_abp = configured_abp + pp_offset_from_center
        logger.debug(
            f"Currently recorded interferograms have peak positions: {computed_pp}"
            + f" ({pp_offset_from_center:+d} points offset from center)"
        )

        # set new peak position
        logger.info(f"Updating peak position from {configured_abp} to {new_abp}")
        interfaces.EM27Interface.set_peak_position(config.opus.em27_ip, new_abp)
