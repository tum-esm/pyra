declare global {
    interface Window {
        electron: {
            checkCLIStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            selectPath: () => Promise<string[] | undefined>;
            playBeep: () => void;
            readSetupJSON: () => Promise<TYPES.setupJSON>;
            saveSetupJSON: (newSetupJSON: string) => Promise<string>;
        };
    }
}

type int_array_3 = [number, number, number];
type int_array_4 = [number, number, number, number];

namespace TYPES {
    export type setupJSON = {
        camtracker: {
            config_path: string;
            executable_path: string;
            learn_az_elev_path: string;
            sun_intensity_path: string;
        };
        em27: {
            ip: string;
        };
        enclosure: {
            tum_enclosure_is_present: boolean;
        };
        opus: {
            executable_path: string;
        };
        plc: {
            actors: {
                current_angle: int_array_4;
                fan_speed: int_array_4;
                move_cover: int_array_4;
                nominal_angle: int_array_4;
            };
            control: {
                auto_temp_mode: int_array_4;
                manual_control: int_array_4;
                manual_temp_mode: int_array_4;
                reset: int_array_4;
                sync_to_tracker: int_array_4;
            };
            ip: string;
            is_present: boolean;
            power: {
                camera: int_array_4;
                computer: int_array_4;
                heater: int_array_4;
                router: int_array_4;
                spectrometer: int_array_4;
            };
            sensors: {
                humidity: int_array_4;
                temperature: int_array_4;
            };
            state: {
                camera: int_array_4;
                computer: int_array_4;
                cover: int_array_4;
                heater: int_array_4;
                motor_failed: int_array_4;
                rain: int_array_4;
                reset_needed: int_array_4;
                router: int_array_4;
                spectrometer: int_array_4;
                ups_alert: int_array_4;
            };
        };
        vbdsd: {
            cam_id: number;
            image_storage_path: string;
            sensor_is_present: boolean;
        };
    };

    export type parametersJSON = {
        camtracker: {
            motor_offset_treshold: number;
        };
        em27: {
            power_min_angle: number;
        };
        opus: {
            executable_parameter: string;
            experiment_path: string;
            macro_path: string;
        };
        pyra: {
            automation_is_running: boolean;
            seconds_per_iteration: number;
            test_mode: boolean;
        };
        vbdsd: {
            evaluation_size: number;
            interval_time: number;
            measurement_threshold: number;
            min_sun_angle: number;
        };
        enclosure: {
            continuous_readings: any[];
            min_sun_angle: number;
        };
        measurement_triggers: {
            type: {
                time: boolean;
                sun_angle: boolean;
                vbdsd: boolean;
                user_control: boolean;
            };
            start_time: int_array_3;
            stop_time: int_array_3;
            user_trigger_present: boolean;
            sun_angle_start: number;
            sun_angle_stop: number;
        };
        measurement_conditions: {
            current_sun_angle: number;
        };
    };
}

export default TYPES;
