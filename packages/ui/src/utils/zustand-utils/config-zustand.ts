import { create } from 'zustand';
import { z } from 'zod';
import { diff } from 'deep-diff';
import { set as lodashSet } from 'lodash';

export const configSchema = z.object({
    general: z.object({
        version: z.string(),
        seconds_per_core_interval: z.union([z.number(), z.string().transform(parseFloat)]),
        test_mode: z.boolean(),
        station_id: z.string(),
        min_sun_elevation: z.union([z.number(), z.string().transform(parseFloat)]),
    }),
    opus: z.object({
        em27_ip: z.string(),
        executable_path: z.string(),
        experiment_path: z.string(),
        macro_path: z.string(),
        username: z.string(),
        password: z.string(),
    }),
    camtracker: z.object({
        config_path: z.string(),
        executable_path: z.string(),
        learn_az_elev_path: z.string(),
        sun_intensity_path: z.string(),
        motor_offset_threshold: z.union([z.number(), z.string().transform(parseFloat)]),
        restart_if_logs_are_too_old: z.boolean(),
    }),
    error_email: z.object({
        smtp_host: z.string(),
        smtp_port: z.number(),
        smtp_username: z.string(),
        smtp_password: z.string(),
        sender_address: z.string(),
        notify_recipients: z.boolean(),
        recipients: z.string(),
    }),
    measurement_decision: z.object({
        mode: z.string(),
        manual_decision_result: z.boolean(),
        cli_decision_result: z.boolean(),
    }),
    measurement_triggers: z.object({
        consider_time: z.boolean(),
        consider_sun_elevation: z.boolean(),
        consider_helios: z.boolean(),
        start_time: z.object({
            hour: z.number(),
            minute: z.number(),
            second: z.number(),
        }),
        stop_time: z.object({
            hour: z.number(),
            minute: z.number(),
            second: z.number(),
        }),
        min_sun_elevation: z.union([z.number(), z.string().transform(parseFloat)]),
    }),
    tum_plc: z
        .object({
            ip: z.string(),
            version: z.number(),
            controlled_by_user: z.boolean(),
        })
        .nullable(),
    helios: z
        .object({
            camera_id: z.number(),
            evaluation_size: z.number(),
            seconds_per_interval: z.union([z.number(), z.string().transform(parseFloat)]),
            edge_detection_threshold: z.union([z.number(), z.string().transform(parseFloat)]),
            save_images: z.boolean(),
        })
        .nullable(),
    upload: z
        .object({
            host: z.string(),
            user: z.string(),
            password: z.string(),
            streams: z.array(
                z.object({
                    is_active: z.boolean(),
                    label: z.string(),
                    variant: z.string(),
                    dated_regex: z.string(),
                    src_directory: z.string(),
                    dst_directory: z.string(),
                    remove_src_after_upload: z.boolean(),
                })
            ),
        })
        .nullable(),
});

export type Config = z.infer<typeof configSchema>;

interface ConfigStore {
    centralConfig: Config | undefined;
    localConfig: Config | undefined;
    setConfig: (c: any) => void;
    setLocalConfigItem: (path: string, value: any) => void;
    setConfigItem: (path: string, value: any) => void;
    configIsDiffering: () => boolean;
}

export const useConfigStore = create<ConfigStore>()((set, state) => ({
    centralConfig: undefined,
    localConfig: undefined,
    setConfig: (c) =>
        set(() => ({ centralConfig: configSchema.parse(c), localConfig: configSchema.parse(c) })),
    setLocalConfigItem: (path, value) =>
        set((state) => {
            if (state.localConfig === undefined || state.centralConfig === undefined) {
                return {};
            } else {
                return {
                    localConfig: lodashSet(state.localConfig, path, value),
                };
            }
        }),
    setConfigItem: (path, value) =>
        set((state) => {
            if (state.localConfig === undefined || state.centralConfig === undefined) {
                return {};
            } else {
                return {
                    localConfig: lodashSet(state.localConfig, path, value),
                    centralConfig: lodashSet(state.centralConfig, path, value),
                };
            }
        }),
    configIsDiffering: () => {
        const currentState = state();
        return diff(currentState.centralConfig, currentState.localConfig) !== undefined;
    },
}));
