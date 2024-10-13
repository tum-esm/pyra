export namespace customTypes {
    export type reduxStateConfig = {
        central: config | undefined;
        local: config | undefined;
        isDiffering: boolean | undefined;
        errorMessage: string | undefined;
    };
    export type reduxState = {
        config: reduxStateConfig;
    };
    export type intArray3 = [number, number, number];
    export type intArray4 = [number, number, number, number];

    export type configSectionKey =
        | 'general'
        | 'opus'
        | 'camtracker'
        | 'error_email'
        | 'measurement_triggers'
        | 'tum_enclosure'
        | 'helios'
        | 'upload';
    export type config = {
        general: {
            version: '4.0.7';
            seconds_per_core_interval: number;
            test_mode: boolean;
            station_id: string;
            min_sun_elevation: number;
        };
        opus: {
            em27_ip: string;
            executable_path: string;
            experiment_path: string;
            macro_path: string;
            username: string;
            password: string;
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
            consider_helios: boolean;
            start_time: { hour: number; minute: number; second: number };
            stop_time: { hour: number; minute: number; second: number };
            min_sun_elevation: number;
        };
        tum_enclosure: null | {
            ip: string;
            version: number;
            controlled_by_user: boolean;
        };
        helios: null | {
            camera_id: number;
            evaluation_size: number;
            seconds_per_interval: number;
            edge_detection_threshold: number;
            save_images: boolean;
        };
        upload: null | {
            host: string;
            user: string;
            password: string;
            upload_ifgs: boolean;
            src_directory_ifgs: string;
            dst_directory_ifgs: string;
            remove_src_ifgs_after_upload: boolean;
            upload_helios: boolean;
            dst_directory_helios: string;
            remove_src_helios_after_upload: boolean;
        };
    };

    // I have not found a more elegant way yet to generate a partialConfig type
    export type partialConfig = {
        general?: {
            version?: '4.0.7';
            seconds_per_core_interval?: number;
            test_mode?: boolean;
            station_id?: string;
            min_sun_elevation?: number;
        };
        opus?: {
            em27_ip?: string;
            executable_path?: string;
            experiment_path?: string;
            macro_path?: string;
            username?: string;
            password?: string;
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
            consider_helios?: boolean;
            start_time?: { hour?: number; minute?: number; second?: number };
            stop_time?: { hour?: number; minute?: number; second?: number };
            min_sun_elevation?: number;
        };
        tum_enclosure?: null | {
            ip?: string;
            version?: number;
            controlled_by_user?: boolean;
        };
        helios?: null | {
            camera_id?: number;
            evaluation_size?: number;
            seconds_per_interval?: number;
            edge_detection_threshold?: number;
            save_images?: boolean;
        };
        upload?: null | {
            host?: string;
            user?: string;
            password?: string;
            upload_ifgs?: boolean;
            src_directory_ifgs?: string;
            dst_directory_ifgs?: string;
            remove_src_ifgs_after_upload?: boolean;
            upload_helios?: boolean;
            dst_directory_helios?: string;
            remove_src_helios_after_upload?: boolean;
        };
    };
}
