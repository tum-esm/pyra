namespace TYPES {
    export type intArray3 = [number, number, number];
    export type intArray4 = [number, number, number, number];

    export type configSectionKey =
        | 'general'
        | 'opus'
        | 'camtracker'
        | 'error_email'
        | 'measurement_triggers'
        | 'tum_plc'
        | 'vbdsd';
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
            version: 1 | 2;
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
            version?: 1 | 2;
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
