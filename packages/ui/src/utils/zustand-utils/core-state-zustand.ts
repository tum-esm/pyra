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
    last_bad_weather_detection: z.number().nullable(),
    tum_enclosure_state: z.object({
        dt: z.string().nullable(),
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
    aemet_enclosure_state: z.object({
        dt: z.string().nullable(),

        // general
        battery_voltage: z.number().nullable(),
        logger_panel_temperature: z.number().nullable(),
        auto_mode: z.number().nullable(),
        enhanced_security_mode: z.number().nullable(),

        // weather sensor readings
        air_pressure_internal: z.number().nullable(),
        air_pressure_external: z.number().nullable(),
        relative_humidity_internal: z.number().nullable(),
        relative_humidity_external: z.number().nullable(),
        air_temperature_internal: z.number().nullable(),
        air_temperature_external: z.number().nullable(),
        dew_point_temperature_internal: z.number().nullable(),
        dew_point_temperature_external: z.number().nullable(),
        wind_direction: z.number().nullable(),
        wind_velocity: z.number().nullable(),
        rain_sensor_counter_1: z.number().nullable(),
        rain_sensor_counter_2: z.number().nullable(),

        // closing reasons
        closed_due_to_rain: z.boolean().nullable(),
        closed_due_to_external_relative_humidity: z.boolean().nullable(),
        closed_due_to_internal_relative_humidity: z.boolean().nullable(),
        closed_due_to_external_air_temperature: z.boolean().nullable(),
        closed_due_to_internal_air_temperature: z.boolean().nullable(),
        closed_due_to_wind_velocity: z.boolean().nullable(),
        opened_due_to_elevated_internal_humidity: z.boolean().nullable(),

        // cover states
        alert_level: z.number().nullable(),
        averia_fault_code: z.number().nullable(),
        cover_status: z.string().nullable(),
        motor_position: z.number().nullable(),

        // other
        em27_has_power: z.boolean().nullable(),
        em27_voltage: z.number().nullable(),
        em27_current: z.number().nullable(),
        em27_power: z.number().nullable(),
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
