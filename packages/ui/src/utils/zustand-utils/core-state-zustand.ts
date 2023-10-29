import { create } from 'zustand';
import { z } from 'zod';

const pyraCoreStateObjectSchema = z.object({
    last_updated: z.string(),
    helios_indicates_good_conditions: z.boolean().nullable(),
    measurements_should_be_running: z.boolean().nullable(),
    plc_state: z.object({
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
    current_exceptions: z.array(z.string()),
    upload_is_running: z.boolean().nullable(),
});

export type PyraCoreStateObject = z.infer<typeof pyraCoreStateObjectSchema>;

interface PyraCoreState {
    pyraCorePid: number | undefined;
    pyraCoreStateObject: PyraCoreStateObject | undefined;
    setPyraCorePid: (pid: number | undefined) => void;
    setPyraCoreStateObject: (stateObject: any) => void;
}

export const usePyraCoreStore = create<PyraCoreState>()((set) => ({
    pyraCorePid: undefined,
    pyraCoreStateObject: undefined,
    setPyraCorePid: (pid) => set(() => ({ pyraCorePid: pid })),
    setPyraCoreStateObject: (stateObject: any) =>
        set(() => ({ pyraCoreStateObject: pyraCoreStateObjectSchema.parse(stateObject) })),
}));
