import { customTypes } from '../../custom-types';

/*
This transformation is necessary because in the interface when typing numbers,
the user might want to type in "1.49". I cannot store the dot in a number variable.
Hence, I need to store it in a string and when passing it to the CLI, this trans-
formation needs to happen.
*/
export default function parseNumberTypes(newConfig: customTypes.config): customTypes.config {
    return {
        general: {
            ...newConfig.general,
            seconds_per_core_interval: parseFloat(`${newConfig.general.seconds_per_core_interval}`),
            min_sun_elevation: parseFloat(`${newConfig.general.min_sun_elevation}`),
        },
        opus: newConfig.opus,
        error_email: newConfig.error_email,
        measurement_decision: newConfig.measurement_decision,
        camtracker: {
            ...newConfig.camtracker,
            motor_offset_threshold: parseFloat(`${newConfig.camtracker.motor_offset_threshold}`),
        },
        measurement_triggers: {
            ...newConfig.measurement_triggers,
            min_sun_elevation: parseFloat(`${newConfig.measurement_triggers.min_sun_elevation}`),
            start_time: {
                hour: parseFloat(`${newConfig.measurement_triggers.start_time.hour}`),
                minute: parseFloat(`${newConfig.measurement_triggers.start_time.minute}`),
                second: parseFloat(`${newConfig.measurement_triggers.start_time.second}`),
            },
            stop_time: {
                hour: parseFloat(`${newConfig.measurement_triggers.stop_time.hour}`),
                minute: parseFloat(`${newConfig.measurement_triggers.stop_time.minute}`),
                second: parseFloat(`${newConfig.measurement_triggers.stop_time.second}`),
            },
        },
        tum_plc:
            newConfig.tum_plc === null
                ? null
                : {
                      ...newConfig.tum_plc,
                      version: parseFloat(`${newConfig.tum_plc.version}`),
                  },
        vbdsd:
            newConfig.vbdsd === null
                ? null
                : {
                      camera_id: parseFloat(`${newConfig.vbdsd.camera_id}`),
                      evaluation_size: parseFloat(`${newConfig.vbdsd.evaluation_size}`),
                      seconds_per_interval: parseFloat(`${newConfig.vbdsd.seconds_per_interval}`),
                      measurement_threshold: parseFloat(`${newConfig.vbdsd.measurement_threshold}`),
                      save_images: newConfig.vbdsd.save_images,
                  },
    };
}
