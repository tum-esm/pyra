export namespace customTypes {
    export type reduxStateConfig = {
        central: config | undefined;
        local: config | undefined;
        isDiffering: boolean | undefined;
    };
    export type reduxStateLogs = {
        infoLines: string[];
        debugLines: string[];
        empty: boolean | undefined;
        loading: boolean;
    };
    export type reduxStateCoreState = {
        content: coreState | undefined;
        loading: boolean;
    };
    export type reduxState = {
        config: reduxStateConfig;
        logs: reduxStateLogs;
        coreState: reduxStateCoreState;
    };
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
            station_id: string;
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
            version: number;
            controlled_by_user: boolean;
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
            station_id?: string;
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
            version?: number;
            controlled_by_user?: boolean;
        };
        vbdsd?: null | {
            camera_id?: number;
            evaluation_size?: number;
            seconds_per_interval?: number;
            measurement_threshold?: number;
            min_sun_elevation?: number;
        };
    };

    export type coreState = {
        automation_should_be_running: boolean;
        enclosure_plc_readings: {
            actors: {
                fan_speed: null | number;
                current_angle: null | number;
            };
            control: {
                auto_temp_mode: null | boolean;
                manual_control: null | boolean;
                manual_temp_mode: null | boolean;
            };
            sensors: {
                humidity: null | number;
                temperature: null | number;
            };
            state: {
                camera: null | boolean;
                computer: null | boolean;
                cover_closed: null | boolean;
                heater: null | boolean;
                motor_failed: null | boolean;
                rain: null | boolean;
                reset_needed: null | boolean;
                router: null | boolean;
                spectrometer: null | boolean;
                ups_alert: null | boolean;
            };
        };
    };
}
