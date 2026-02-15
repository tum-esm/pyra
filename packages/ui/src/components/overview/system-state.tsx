import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { mean } from 'lodash';
import { renderBoolean, renderString, renderNumber } from '../../utils/functions';
import { IconCloudRain } from '@tabler/icons-react';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';

function StatePanel(props: { title: string; children: React.ReactNode }) {
    return (
        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
            <div className="text-xs font-semibold">{props.title}</div>
            <div className="flex flex-row items-center gap-x-2">{props.children}</div>
        </div>
    );
}

function StateBarPanel(props: { title: string; value: number | null }) {
    return (
        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
            <div className="text-xs font-semibold">{props.title}</div>
            <div className="flex flex-row items-center gap-x-2">
                {props.value ? (
                    <>
                        <div className="min-w-12 whitespace-nowrap">
                            {props.value.toFixed(1) + ' %'}
                        </div>
                        <div className="relative flex-grow h-2 overflow-hidden rounded-full bg-slate-200">
                            <div
                                className="absolute top-0 bottom-0 left-0 bg-slate-500"
                                style={{
                                    width: `${props.value}%`,
                                }}
                            />
                        </div>
                    </>
                ) : (
                    '-'
                )}
            </div>
        </div>
    );
}

export function SystemState() {
    const { coreState } = useCoreStateStore();
    const { centralConfig } = useConfigStore();
    const { coreLogs } = useLogsStore();

    if (!coreState || !centralConfig || !coreLogs.helios) {
        return <></>;
    }

    // heliosLogs contain the string "edge_fraction = 0.0"
    // look for the last occurence of this string using regex
    const lastEdgeFraction = coreLogs.helios
        .join('\n')
        .match(/edge_fraction = \d+(\.\d+)?\s*\n/g)
        ?.slice(-1)[0];
    const lastEdgeFractionValue = lastEdgeFraction
        ? parseFloat(lastEdgeFraction.split(' ')[2])
        : null;

    let weatherWarning: string | null = null;
    if (
        coreState?.tum_enclosure_state.state.rain === true &&
        coreState?.tum_enclosure_state.state.cover_closed === false
    ) {
        weatherWarning = 'Rain has been detected but cover is not closed';
    } else if (
        (coreState?.aemet_enclosure_state.closed_due_to_rain ||
            coreState?.aemet_enclosure_state.closed_due_to_external_relative_humidity ||
            coreState?.aemet_enclosure_state.closed_due_to_internal_relative_humidity ||
            coreState?.aemet_enclosure_state.closed_due_to_internal_air_temperature ||
            coreState?.aemet_enclosure_state.closed_due_to_external_air_temperature ||
            coreState?.aemet_enclosure_state.closed_due_to_wind_velocity) &&
        coreState?.aemet_enclosure_state.cover_status !== 'C'
    ) {
        weatherWarning = 'Bad weather conditions have been detected but cover is not closed';
    }

    return (
        <>
            {centralConfig.tum_enclosure !== null && (
                <div className="grid w-full grid-cols-6 px-4 pb-1 text-sm gap-x-1">
                    <StatePanel title="Cover Angle">
                        {renderString(coreState.tum_enclosure_state.actors.current_angle, {
                            appendix: ' °',
                        })}
                    </StatePanel>
                    <StatePanel title="Temperature">
                        {renderString(coreState.tum_enclosure_state.sensors.temperature, {
                            appendix: ' °C',
                        })}
                    </StatePanel>
                    <StatePanel title="Humidity">
                        {renderString(coreState.tum_enclosure_state.sensors.humidity, {
                            appendix: ' rH',
                        })}
                    </StatePanel>
                    <StatePanel title="Heater Power">
                        {renderBoolean(coreState.tum_enclosure_state.power.heater)}
                    </StatePanel>
                    <StatePanel title="Rain Detected">
                        {renderBoolean(coreState.tum_enclosure_state.state.rain)}
                    </StatePanel>
                    <StatePanel title="Helios Edge Pixels">
                        {renderNumber(
                            lastEdgeFractionValue === null ? null : lastEdgeFractionValue * 100,
                            { appendix: ' %' }
                        )}
                    </StatePanel>
                </div>
            )}
            {centralConfig.aemet_enclosure !== null && (
                <div className="grid w-full grid-cols-4 px-4 pb-1 text-sm gap-x-1">
                    <StatePanel title="Alert Level">
                        {renderNumber(coreState.aemet_enclosure_state.alert_level)}
                    </StatePanel>
                    <StatePanel title="Averia Fault Code">
                        {renderNumber(coreState.aemet_enclosure_state.averia_fault_code)}
                    </StatePanel>
                    <StatePanel title="Cover Status">
                        {renderString(coreState.aemet_enclosure_state.cover_status)}
                    </StatePanel>
                    <StatePanel title="Motor Position">
                        {renderNumber(coreState.aemet_enclosure_state.motor_position)}
                    </StatePanel>

                    {/* closing reasons RAIN */}
                    <StatePanel title="Closed Due To Rain">
                        {renderBoolean(coreState.aemet_enclosure_state.closed_due_to_rain)}
                    </StatePanel>
                    <StatePanel title="Rain Sensor Counter 1">
                        {renderNumber(coreState.aemet_enclosure_state.rain_sensor_counter_1)}
                    </StatePanel>
                    <StatePanel title="Rain Sensor Counter 2">
                        {renderNumber(coreState.aemet_enclosure_state.rain_sensor_counter_2)}
                    </StatePanel>
                    <StatePanel title="Helios Edge Pixels">
                        {renderNumber(
                            lastEdgeFractionValue === null ? null : lastEdgeFractionValue * 100,
                            { appendix: ' %' }
                        )}
                    </StatePanel>

                    {/* closing reasons HUMIDITY */}
                    <StatePanel title="Closed Due To Internal rH">
                        {renderBoolean(
                            coreState.aemet_enclosure_state.closed_due_to_internal_relative_humidity
                        )}
                    </StatePanel>
                    <StatePanel title="Closed Due To External rH">
                        {renderBoolean(
                            coreState.aemet_enclosure_state.closed_due_to_external_relative_humidity
                        )}
                    </StatePanel>

                    <StatePanel title="Internal rH">
                        {renderNumber(coreState.aemet_enclosure_state.relative_humidity_internal, {
                            appendix: ' %',
                        })}
                    </StatePanel>
                    <StatePanel title="External rH">
                        {renderNumber(coreState.aemet_enclosure_state.relative_humidity_external, {
                            appendix: ' %',
                        })}
                    </StatePanel>

                    {/* closing reasons TEMPERATURE */}
                    <StatePanel title="Closed Due To Internal Temp.">
                        {renderBoolean(
                            coreState.aemet_enclosure_state.closed_due_to_internal_air_temperature
                        )}
                    </StatePanel>
                    <StatePanel title="Closed Due To External Temp.">
                        {renderBoolean(
                            coreState.aemet_enclosure_state.closed_due_to_external_air_temperature
                        )}
                    </StatePanel>
                    <StatePanel title="Internal Air Temperature">
                        {renderNumber(coreState.aemet_enclosure_state.air_temperature_internal, {
                            appendix: ' °C',
                        })}
                    </StatePanel>
                    <StatePanel title="External Air Temperature">
                        {renderNumber(coreState.aemet_enclosure_state.air_temperature_external, {
                            appendix: ' °C',
                        })}
                    </StatePanel>

                    {/* closing reasons WIND */}
                    <StatePanel title="Closed Due to Wind Speed.">
                        {renderBoolean(coreState.aemet_enclosure_state.closed_due_to_wind_velocity)}
                    </StatePanel>
                    <StatePanel title="Wind Speed">
                        {renderNumber(coreState.aemet_enclosure_state.wind_velocity, {
                            appendix: ' m/s',
                        })}
                    </StatePanel>
                    <StatePanel title="Wind Direction">
                        {renderNumber(coreState.aemet_enclosure_state.wind_direction, {
                            appendix: ' °',
                        })}
                    </StatePanel>

                    <StatePanel title="Opened Due to Elevated Internal rH">
                        {renderBoolean(
                            coreState.aemet_enclosure_state.opened_due_to_elevated_internal_humidity
                        )}
                    </StatePanel>

                    {/* other environmental parameters */}
                    <StatePanel title="Internal Pressure">
                        {renderNumber(coreState.aemet_enclosure_state.air_pressure_internal, {
                            appendix: ' hPa',
                        })}
                    </StatePanel>
                    <StatePanel title="External Pressure">
                        {renderNumber(coreState.aemet_enclosure_state.air_pressure_external, {
                            appendix: ' hPa',
                        })}
                    </StatePanel>
                    <StatePanel title="Internal Dew Point Temp.">
                        {renderNumber(
                            coreState.aemet_enclosure_state.dew_point_temperature_internal,
                            {
                                appendix: ' °C',
                            }
                        )}
                    </StatePanel>
                    <StatePanel title="External Dew Point Temp.">
                        {renderNumber(
                            coreState.aemet_enclosure_state.dew_point_temperature_external,
                            {
                                appendix: ' °C',
                            }
                        )}
                    </StatePanel>
                </div>
            )}
            {weatherWarning !== null && (
                <div className="w-full px-4 mb-4 -mt-2 text-sm">
                    <div
                        className={
                            'flex w-full flex-row items-center flex-grow p-3 font-medium rounded-lg gap-x-2 text-red-50 bg-red-500'
                        }
                    >
                        <IconCloudRain size={20} />
                        <div>{weatherWarning}</div>
                    </div>
                </div>
            )}
            <div className="grid w-full grid-cols-4 px-4 pb-4 text-sm gap-x-1 gap-y-1">
                <StatePanel title="Last Boot Time">
                    {coreState.operating_system_state.last_boot_time}
                </StatePanel>
                <StateBarPanel
                    title="Disk Usage"
                    value={coreState.operating_system_state.filled_disk_space_fraction}
                />
                <StateBarPanel
                    title="CPU Usage"
                    value={
                        coreState.operating_system_state.cpu_usage
                            ? mean(coreState.operating_system_state.cpu_usage)
                            : null
                    }
                />
                <StateBarPanel
                    title="Memory Usage"
                    value={coreState.operating_system_state.memory_usage}
                />
                <StatePanel title="Latitude">
                    {renderString(coreState.position.latitude, {
                        appendix: ' °N',
                    })}
                </StatePanel>
                <StatePanel title="Longitude">
                    {renderString(coreState?.position.longitude, {
                        appendix: ' °E',
                    })}
                </StatePanel>
                <StatePanel title="Altitude">
                    {renderString(coreState?.position.altitude, {
                        appendix: ' m',
                    })}
                </StatePanel>
                <StatePanel title="Sun Elevation">
                    {renderString(coreState?.position.sun_elevation, {
                        appendix: ' °',
                    })}
                </StatePanel>
            </div>
        </>
    );
}
