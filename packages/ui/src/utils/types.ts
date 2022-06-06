namespace TYPES {
    export type intArray3 = [number, number, number];
    export type intArray4 = [number, number, number, number];

    export type config = {
        general: {
            seconds_per_core_interval: number;
            test_mode: boolean;
        };
        opus: {
            em27_ip: string;
            executable_path: string;
            executable_parameter: string;
            experiment_path: string;
            macro_path: string;
        };
        camtracker: {
            config_path: string;
            executable_path: string;
            learn_az_elev_path: string;
            sun_intensity_path: string;
            motor_offset_threshold: number;
        };
        error_email: {
            sender_address: string;
            sender_password: string;
            notify_recipients: boolean;
            recipients: string;
        };
        measurement_decision: {
            mode: 'automatic' | 'manual' | 'cli';
            manual_decision_result: boolean;
            cli_decision_result: boolean;
        };
        measurement_triggers: {
            consider_time: boolean;
            consider_sun_elevation: boolean;
            consider_vbdsd: boolean;
            start_time: { hour: number; minute: number; second: number };
            stop_time: { hour: number; minute: number; second: number };
            min_sun_elevation: number;
            max_sun_elevation: number;
        };
        tum_plc: null | {
            min_power_elevation: number;
            ip: string;
            actors: {
                current_angle: intArray3;
                fan_speed: intArray3;
                move_cover: intArray3;
                nominal_angle: intArray3;
            };
            control: {
                auto_temp_mode: intArray4;
                manual_control: intArray4;
                manual_temp_mode: intArray4;
                reset: intArray4;
                sync_to_tracker: intArray4;
            };
            power: {
                camera: intArray4;
                computer: intArray4;
                heater: intArray4;
                router: intArray4;
                spectrometer: intArray4;
            };
            sensors: {
                humidity: intArray3;
                temperature: intArray3;
            };
            state: {
                camera: intArray4;
                computer: intArray4;
                cover_closed: intArray4;
                heater: intArray4;
                motor_failed: intArray4;
                rain: intArray4;
                reset_needed: intArray4;
                router: intArray4;
                spectrometer: intArray4;
                ups_alert: intArray4;
            };
        };
        vbdsd: null | {
            camera_id: number;
            evaluation_size: number;
            seconds_per_interval: number;
            measurement_threshold: number;
            min_sun_elevation: number;
        };
    };

    // I have not found a more elegant way yet to generate a partialConfig type
    export type partialConfig = {
        general?: {
            seconds_per_core_interval?: number;
            test_mode?: boolean;
        };
        opus?: {
            em27_ip?: string;
            executable_path?: string;
            executable_parameter?: string;
            experiment_path?: string;
            macro_path?: string;
        };
        camtracker?: {
            config_path?: string;
            executable_path?: string;
            learn_az_elev_path?: string;
            sun_intensity_path?: string;
            motor_offset_threshold?: number;
        };
        error_email?: {
            sender_address?: string;
            sender_password?: string;
            notify_recipients?: boolean;
            recipients?: string;
        };
        measurement_decision?: {
            mode?: 'automatic' | 'manual' | 'cli';
            manual_decision_result?: boolean;
            cli_decision_result?: boolean;
        };
        measurement_triggers?: {
            consider_time?: boolean;
            consider_sun_elevation?: boolean;
            consider_vbdsd?: boolean;
            start_time?: { hour?: number; minute?: number; second?: number };
            stop_time?: { hour?: number; minute?: number; second?: number };
            min_sun_elevation?: number;
            max_sun_elevation?: number;
        };
        tum_plc?: null | {
            min_power_elevation?: number;
            ip?: string;
            actors?: {
                current_angle?: intArray3;
                fan_speed?: intArray3;
                move_cover?: intArray3;
                nominal_angle?: intArray3;
            };
            control?: {
                auto_temp_mode?: intArray4;
                manual_control?: intArray4;
                manual_temp_mode?: intArray4;
                reset?: intArray4;
                sync_to_tracker?: intArray4;
            };
            power?: {
                camera?: intArray4;
                computer?: intArray4;
                heater?: intArray4;
                router?: intArray4;
                spectrometer?: intArray4;
            };
            sensors?: {
                humidity?: intArray3;
                temperature?: intArray3;
            };
            state?: {
                camera?: intArray4;
                computer?: intArray4;
                cover_closed?: intArray4;
                heater?: intArray4;
                motor_failed?: intArray4;
                rain?: intArray4;
                reset_needed?: intArray4;
                router?: intArray4;
                spectrometer?: intArray4;
                ups_alert?: intArray4;
            };
        };
        vbdsd?: null | {
            camera_id?: number;
            evaluation_size?: number;
            seconds_per_interval?: number;
            measurement_threshold?: number;
            min_sun_elevation?: number;
        };
    };
}

export default TYPES;
