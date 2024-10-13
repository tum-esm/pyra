import { create } from 'zustand';
import { z } from 'zod';
import { set as lodashSet } from 'lodash';

const coreStateSchema = z.object({
    position: z.object({
        latitude: z.number().nullable(),
        longitude: z.number().nullable(),
        altitude: z.number().nullable(),
        sun_elevation: z.number().nullable(),
    }),
    measurements_should_be_running: z.boolean().nullable(),
    tum_enclosure_state: z.object({
        last_full_fetch: z.string().nullable(),
        actors: z.object({
            fan_speed: z.number().nullable(),
            current_angle: z.number().nullable(),
        }),
        control: z.object({
            auto_temp_mode: z.boolean().nullable(),
            manual_control: z.boolean().nullable(),
            manual_temp_mode: z.boolean().nullable(),
            sync_to_tracker: z.boolean().nullable(),
        }),
        sensors: z.object({
            humidity: z.number().nullable(),
            temperature: z.number().nullable(),
        }),
        state: z.object({
            cover_closed: z.boolean().nullable(),
            motor_failed: z.boolean().nullable(),
            rain: z.boolean().nullable(),
            reset_needed: z.boolean().nullable(),
            ups_alert: z.boolean().nullable(),
        }),
        power: z.object({
            camera: z.boolean().nullable(),
            computer: z.boolean().nullable(),
            heater: z.boolean().nullable(),
            router: z.boolean().nullable(),
            spectrometer: z.boolean().nullable(),
        }),
        connections: z.object({
            camera: z.boolean().nullable(),
            computer: z.boolean().nullable(),
            heater: z.boolean().nullable(),
            router: z.boolean().nullable(),
            spectrometer: z.boolean().nullable(),
        }),
    }),
    operating_system_state: z.object({
        cpu_usage: z.array(z.number()).nullable(),
        memory_usage: z.number().nullable(),
        last_boot_time: z.string().nullable(),
        filled_disk_space_fraction: z.number().nullable(),
    }),
});

export type CoreState = z.infer<typeof coreStateSchema>;

interface CoreStateStore {
    coreState: CoreState | undefined;
    setCoreState: (s: any) => void;
    setCoreStateItem: (path: string, value: any) => void;
}

export const useCoreStateStore = create<CoreStateStore>()((set) => ({
    coreState: undefined,
    setCoreState: (s: any) => set(() => ({ coreState: coreStateSchema.parse(s) })),
    setCoreStateItem: (path: string, value: any) =>
        set((state) => {
            if (state.coreState === undefined) {
                return {};
            }
            return {
                coreState: lodashSet(state.coreState, path, value),
            };
        }),
}));
