export namespace customTypes {
    export type reduxStateConfig = {
        central: config | undefined;
        local: config | undefined;
        isDiffering: boolean | undefined;
        errorMessage: string | undefined;
    };
    export type reduxStateLogs = {
        infoLines: string[] | undefined;
        debugLines: string[] | undefined;
        fetchUpdates: boolean;
        renderedLogScope: string;
    };
    export type reduxStateCoreState = { body: coreState | undefined };
    export type reduxStateCoreProcess = {
        pid: number | undefined;
    };
    export type reduxState = {
        config: reduxStateConfig;
        logs: reduxStateLogs;
        coreState: reduxStateCoreState;
        coreProcess: reduxStateCoreProcess;
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
            save_images: boolean;
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
            save_images?: boolean;
        };
    };

    export type enclosurePlcReadings = {
        actors: {
            fan_speed: number | null;
            current_angle: number | null;
        };
        control: {
            auto_temp_mode: boolean | null;
            manual_control: boolean | null;
            manual_temp_mode: boolean | null;
            sync_to_tracker: boolean | null;
        };
        sensors: {
            humidity: number | null;
            temperature: number | null;
        };
        state: {
            cover_closed: boolean | null;
            motor_failed: boolean | null;
            rain: boolean | null;
            reset_needed: boolean | null;
            ups_alert: boolean | null;
        };
        power: {
            camera: boolean | null;
            computer: boolean | null;
            heater: boolean | null;
            router: boolean | null;
            spectrometer: boolean | null;
        };
        connections: {
            camera: boolean | null;
            computer: boolean | null;
            heater: boolean | null;
            router: boolean | null;
            spectrometer: boolean | null;
        };
    };

    export type partialEnclosurePlcReadings = {
        actors?: {
            fan_speed?: number;
            current_angle?: number;
        };
        control?: {
            auto_temp_mode?: boolean;
            manual_control?: boolean;
            manual_temp_mode?: boolean;
            sync_to_tracker?: boolean;
        };
        sensors?: {
            humidity?: number;
            temperature?: number;
        };
        state?: {
            cover_closed?: boolean;
            motor_failed?: boolean;
            rain?: boolean;
            reset_needed?: boolean;
            ups_alert?: boolean;
        };
        power?: {
            camera?: boolean;
            computer?: boolean;
            heater?: boolean;
            router?: boolean;
            spectrometer?: boolean;
        };
        connections?: {
            camera?: boolean;
            computer?: boolean;
            heater?: boolean;
            router?: boolean;
            spectrometer?: boolean;
        };
    };

    export type OSState = {
        cpu_usage: number | null;
        memory_usage: number | null;
        last_boot_time: string | null;
        filled_disk_space_fraction: number | null;
    };

    export type coreState = {
        vbdsd_indicates_good_conditions: boolean | null;
        measurements_should_be_running: boolean;
        enclosure_plc_readings: enclosurePlcReadings;
        os_state: OSState;
    };

    export type partialCoreState = {
        measurements_should_be_running?: boolean;
        enclosure_plc_readings?: partialEnclosurePlcReadings;
    };
}
