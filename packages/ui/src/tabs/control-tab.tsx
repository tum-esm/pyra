import { fetchUtils } from '../utils';
import { essentialComponents } from '../components';
import { ICONS } from '../assets';
import toast from 'react-hot-toast';
import { useCoreStateStore } from '../utils/zustand-utils/core-state-zustand';
import { useConfigStore } from '../utils/zustand-utils/config-zustand';

function renderBoolValue(value: boolean | null) {
    if (value === null) {
        return '-';
    }
    return value ? 'Yes' : 'No';
}

function renderStringValue(value: string | number | null, postfix: string) {
    if (value === null) {
        return '-';
    }
    return `${value} ${postfix}`;
}

const COVERR_STATUS_MAP: Record<string, string> = {
    AF: 'opening lock',
    'A.': 'opening hood',
    A: 'open',
    'C.': 'closing hood',
    CF: 'closing lock',
    C: 'closed',
};

function VariableBlock(props: {
    label: string;
    disabled: boolean;
    rows: {
        variable: { key: string; value: string | number };
        action?:
            | {
                  label: string;
                  callback: (value: number) => void;
                  variant: 'numeric';
                  initialValue: number;
                  postfix?: string;
              }
            | { label: string; callback: () => void; variant?: undefined };
    }[];
}) {
    return (
        <div className="relative flex flex-col flex-shrink-0 overflow-hidden divide-y divide-blue-200">
            <div className="flex items-center flex-shrink-0 w-full px-3 py-1 text-sm font-semibold bg-blue-100 text-blue-950">
                {props.label}
            </div>
            <div className="flex-grow bg-white divide-y divide-slate-100 flex-col-left">
                {props.rows.map((r, i) => (
                    <div
                        className="flex flex-row items-center justify-center w-full px-3 text-sm h-11"
                        key={i}
                    >
                        <div className="w-72 font-base">{r.variable.key}:</div>{' '}
                        <div className="w-20 font-semibold text-right">{r.variable.value}</div>
                        <div className="flex-grow" />
                        {r.action && r.variable.value !== '-' && (
                            <>
                                {r.action.variant === undefined && (
                                    <essentialComponents.Button
                                        variant="white"
                                        onClick={r.action.callback}
                                        key={r.action.label}
                                        className="w-60"
                                        disabled={props.disabled}
                                    >
                                        {r.action.label}
                                    </essentialComponents.Button>
                                )}{' '}
                                {r.action.variant !== undefined && (
                                    <essentialComponents.NumericButton
                                        initialValue={r.action.initialValue}
                                        onClick={r.action.callback}
                                        key={r.action.label}
                                        className="w-60"
                                        postfix={r.action.postfix}
                                        disabled={props.disabled}
                                    >
                                        {r.action.label}
                                    </essentialComponents.NumericButton>
                                )}
                            </>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

function HeaderBlock(props: {
    plcIsControlledByUser: boolean;
    setPlcIsControlledByUser: (v: boolean) => void;
    lastEnclosureStateRead: string | null;
}) {
    return (
        <div className="z-10 flex-shrink-0 w-full h-16 px-4 py-4 bg-white border-b flex-row-left gap-x-2 border-slate-300">
            <essentialComponents.Toggle
                value={props.plcIsControlledByUser ? 'user controlled' : 'automatic'}
                values={['user controlled', 'automatic']}
                setValue={(v) => props.setPlcIsControlledByUser(v === 'user controlled')}
            />
            <div className="text-sm text-gray-500 flex-row-center">
                {props.plcIsControlledByUser && 'The automation will skip all PLC related logic'}
                {!props.plcIsControlledByUser && 'You cannot send any commands to the PLC'}
            </div>
            <div className="flex-grow" />
            <div className="text-sm text-slate-700">
                Last PLC-read:{' '}
                {props.lastEnclosureStateRead === null ? '-' : props.lastEnclosureStateRead}
            </div>
        </div>
    );
}

export function TUMEnclosureControlTab() {
    const { coreState } = useCoreStateStore();
    const { centralConfig, setConfigItem } = useConfigStore();
    const { setCoreStateItem } = useCoreStateStore();
    const enclosureIsControlledByUser = centralConfig?.tum_enclosure?.controlled_by_user;

    const { commandIsRunning, runPromisingCommand } = fetchUtils.useCommand();
    const buttonsAreDisabled = !enclosureIsControlledByUser || commandIsRunning;

    async function setEnclosureIsControlledByUser(v: boolean) {
        runPromisingCommand({
            command: () =>
                fetchUtils.backend.updateConfig({ tum_enclosure: { controlled_by_user: v } }),
            label: 'toggling enclosure control mode',
            successLabel: 'successfully toggled enclosure control mode',
            onSuccess: () => setConfigItem('tum_enclosure.controlled_by_user', v),
        });
    }

    async function runPLCCommand(
        command: string[],
        label: string,
        successLabel: string,
        onSuccess: () => void
    ) {
        runPromisingCommand({
            command: () => fetchUtils.backend.writeToTUMEnclosure(command),
            label: label,
            successLabel: successLabel,
            onSuccess: onSuccess,
        });
    }

    async function reset() {
        await runPLCCommand(['reset'], 'running PLC reset', 'successfully reset the PLC', () =>
            setCoreStateItem('tum_enclosure_state.reset_needed', false)
        );
    }

    async function closeCover() {
        await runPLCCommand(['close-cover'], 'closing cover', 'successfully closed cover', () => {
            setCoreStateItem('tum_enclosure_state.state.cover_closed', true);
            setCoreStateItem('tum_enclosure_state.actors.current_angle', 0);
        });
    }

    async function moveCover(angle: number) {
        if (angle === 0 || (angle >= 110 && angle <= 250)) {
            await runPLCCommand(
                ['set-cover-angle', `${angle}`],
                'moving cover',
                'successfully moved cover',
                () => {
                    setCoreStateItem('tum_enclosure_state.state.cover_closed', angle === 0);
                    setCoreStateItem('tum_enclosure_state.actors.current_angle', angle);
                }
            );
        } else {
            toast.error(`Angle has to be either 0 or between 110° and 250°`);
        }
    }

    async function toggleSyncToTracker() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.control.sync_to_tracker;
            await runPLCCommand(
                ['set-sync-to-tracker', JSON.stringify(newValue)],
                'toggling sync-to-tracker',
                'successfully toggled sync-to-tracker',
                () => setCoreStateItem('tum_enclosure_state.control.sync_to_tracker', newValue)
            );
        }
    }

    async function toggleAutoTemperature() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.control.auto_temp_mode;
            await runPLCCommand(
                ['set-auto-temperature', JSON.stringify(newValue)],
                'toggling auto-temperature',
                'successfully toggled auto-temperature',
                () => setCoreStateItem('tum_enclosure_state.control.auto_temp_mode', newValue)
            );
        }
    }

    async function togglePowerHeater() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.power.heater;
            await runPLCCommand(
                ['set-heater-power', JSON.stringify(newValue)],
                'toggling heater power',
                'successfully toggled heater power',
                () => setCoreStateItem('tum_enclosure_state.power.heater', newValue)
            );
        }
    }

    async function togglePowerCamera() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.power.camera;
            await runPLCCommand(
                ['set-camera-power', JSON.stringify(newValue)],
                'toggling camera power',
                'successfully toggled camera power',
                () => setCoreStateItem('tum_enclosure_state.power.camera', newValue)
            );
        }
    }

    async function togglePowerRouter() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.power.router;
            await runPLCCommand(
                ['set-router-power', JSON.stringify(newValue)],
                'toggling router power',
                'successfully toggled router power',
                () => setCoreStateItem('tum_enclosure_state.power.router', newValue)
            );
        }
    }

    async function togglePowerSpectrometer() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.power.spectrometer;
            await runPLCCommand(
                ['set-spectrometer-power', JSON.stringify(newValue)],
                'toggling spectrometer power',
                'successfully toggled spectrometer power',
                () => setCoreStateItem('tum_enclosure_state.power.spectrometer', newValue)
            );
        }
    }

    async function togglePowerComputer() {
        if (coreState !== undefined) {
            const newValue = !coreState.tum_enclosure_state.power.computer;
            await runPLCCommand(
                ['set-computer-power', JSON.stringify(newValue)],
                'toggling computer power',
                'successfully toggled computer power',
                () => setCoreStateItem('tum_enclosure_state.power.computer', newValue)
            );
        }
    }

    if (coreState === undefined || centralConfig === undefined) {
        return <></>;
    }

    return (
        <div className={'w-full h-[calc(100vh-3.5rem)] relative flex-col-left'}>
            <HeaderBlock
                plcIsControlledByUser={enclosureIsControlledByUser || false}
                setPlcIsControlledByUser={setEnclosureIsControlledByUser}
                lastEnclosureStateRead={
                    coreState.tum_enclosure_state.dt === null ||
                    coreState.tum_enclosure_state.dt === undefined
                        ? null
                        : coreState.tum_enclosure_state.dt
                }
            />
            <div className="flex flex-col flex-1 w-full overflow-y-scroll text-sm divide-y divide-blue-200 h-[calc(100vh-7.5rem)]">
                <VariableBlock
                    label="Errors"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Reset needed',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.state.reset_needed
                                ),
                            },
                            action: {
                                label: 'reset now',
                                callback: reset,
                            },
                        },
                        {
                            variable: {
                                key: 'Motor failed',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.state.motor_failed
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'UPS alert',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.state.ups_alert
                                ),
                            },
                        },
                    ]}
                />

                <VariableBlock
                    label="Rain Detection"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Cover is closed',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.state.cover_closed
                                ),
                            },
                            action: {
                                label: 'force cover close',
                                callback: closeCover,
                            },
                        },
                        {
                            variable: {
                                key: 'Rain detected',
                                value: renderBoolValue(coreState.tum_enclosure_state.state.rain),
                            },
                        },
                    ]}
                />

                <VariableBlock
                    label="Cover Angle"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Current cover angle',
                                value: renderStringValue(
                                    coreState.tum_enclosure_state.actors.current_angle,
                                    '°'
                                ),
                            },
                            action: {
                                label: 'move to angle',
                                callback: moveCover,
                                variant: 'numeric',
                                initialValue:
                                    coreState.tum_enclosure_state.actors.current_angle || 0,
                                postfix: '°',
                            },
                        },
                        {
                            variable: {
                                key: 'Sync to CamTracker',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.control.sync_to_tracker
                                ),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.control.sync_to_tracker
                                    ? 'do not sync'
                                    : 'sync',
                                callback: toggleSyncToTracker,
                            },
                        },
                    ]}
                />

                <VariableBlock
                    label="Climate"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Temperature',
                                value: renderStringValue(
                                    coreState.tum_enclosure_state.sensors.temperature,
                                    ' °C'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Humidity',
                                value: renderStringValue(
                                    coreState.tum_enclosure_state.sensors.humidity,
                                    '%'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Fan Speed',
                                value: renderStringValue(
                                    coreState.tum_enclosure_state.actors.fan_speed,
                                    '%'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Auto temperature',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.control.auto_temp_mode
                                ),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.control.auto_temp_mode
                                    ? 'disable'
                                    : 'enable',
                                callback: toggleAutoTemperature,
                            },
                        },
                    ]}
                />

                <VariableBlock
                    label="Power"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Camera Power',
                                value: renderBoolValue(coreState.tum_enclosure_state.power.camera),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.power.camera
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerCamera,
                            },
                        },
                        {
                            variable: {
                                key: 'Router Power',
                                value: renderBoolValue(coreState.tum_enclosure_state.power.router),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.power.router
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerRouter,
                            },
                        },
                        {
                            variable: {
                                key: 'Spectrometer Power',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.power.spectrometer
                                ),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.power.spectrometer
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerSpectrometer,
                            },
                        },
                        {
                            variable: {
                                key: 'Computer Power',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.power.computer
                                ),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.power.computer
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerComputer,
                            },
                        },
                        {
                            variable: {
                                key: 'Heater power',
                                value: renderBoolValue(coreState.tum_enclosure_state.power.heater),
                            },
                            action: {
                                label: coreState.tum_enclosure_state.power.heater
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerHeater,
                            },
                        },
                    ]}
                />

                <VariableBlock
                    label="Connections"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Camera',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.connections.camera
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Computer',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.connections.computer
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Heater',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.connections.heater
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Router',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.connections.router
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Spectrometer',
                                value: renderBoolValue(
                                    coreState.tum_enclosure_state.connections.spectrometer
                                ),
                            },
                        },
                    ]}
                />
            </div>
        </div>
    );
}

export function AEMETEnclosureControlTab() {
    const { coreState } = useCoreStateStore();
    const { centralConfig, setConfigItem } = useConfigStore();
    const { setCoreStateItem } = useCoreStateStore();
    const enclosureIsControlledByUser = centralConfig?.aemet_enclosure?.controlled_by_user;

    const { commandIsRunning, runPromisingCommand } = fetchUtils.useCommand();
    const buttonsAreDisabled = !enclosureIsControlledByUser || commandIsRunning;

    async function setEnclosureIsControlledByUser(v: boolean) {
        runPromisingCommand({
            command: () =>
                fetchUtils.backend.updateConfig({ aemet_enclosure: { controlled_by_user: v } }),
            label: 'toggling enclosure control mode',
            successLabel: 'successfully toggled enclosure control mode',
            onSuccess: () => setConfigItem('aemet_enclosure.controlled_by_user', v),
        });
    }

    async function runPLCCommand(
        command: string[],
        label: string,
        successLabel: string,
        onSuccess: () => void
    ) {
        runPromisingCommand({
            command: () => fetchUtils.backend.writeToAEMETEnclosure(command),
            label: label,
            successLabel: successLabel,
            onSuccess: onSuccess,
        });
    }

    async function openCover() {
        await runPLCCommand(['open-cover'], 'opening cover', 'successfully opened cover', () => {
            setCoreStateItem('aemet_enclosure_state.cover_state', 'A');
        });
    }

    async function closeCover() {
        await runPLCCommand(['close-cover'], 'closing cover', 'successfully closed cover', () => {
            setCoreStateItem('aemet_enclosure_state.cover_state', 'C');
        });
    }

    async function setAutoMode(value: number) {
        await runPLCCommand(
            ['set-auto-mode', `${value}`],
            'setting auto mode',
            `successfully set auto mode to ${value}`,
            () => {
                setCoreStateItem('aemet_enclosure_state.auto_mode', value);
            }
        );
    }

    async function setAlertLevel(value: number) {
        await runPLCCommand(
            ['set-alert-level', `${value}`],
            'setting alert level',
            `successfully set alert level to ${value}`,
            () => {
                setCoreStateItem('aemet_enclosure_state.alert_level', value);
            }
        );
    }

    async function setAveriaFaultCode(value: number) {
        await runPLCCommand(
            ['set-averia-fault-code', `${value}`],
            'setting averia fault code',
            `successfully set averia fault code to ${value}`,
            () => {
                setCoreStateItem('aemet_enclosure_state.averia_fault_code', value);
            }
        );
    }

    async function setEnhancedSecurityMode(value: number) {
        await runPLCCommand(
            ['set-enhanced-security-mode', `${value}`],
            'setting enhanced security mode',
            `successfully set enhanced security mode to ${value}`,
            () => {
                setCoreStateItem('aemet_enclosure_state.enhanced_security_mode', value);
            }
        );
    }

    async function togglePowerSpectrometer() {
        if (coreState !== undefined) {
            const newValue = !coreState.aemet_enclosure_state.em27_has_power;
            await runPLCCommand(
                ['set-spectrometer-power', JSON.stringify(newValue)],
                'toggling spectrometer power',
                'successfully toggled spectrometer power',
                () => setCoreStateItem('aemet_enclosure_state.em27_has_power', newValue)
            );
        }
    }

    if (coreState === undefined || centralConfig === undefined) {
        return <></>;
    }

    return (
        <div className={'w-full h-[calc(100vh-3.5rem)] relative flex-col-left'}>
            <HeaderBlock
                plcIsControlledByUser={enclosureIsControlledByUser || false}
                setPlcIsControlledByUser={setEnclosureIsControlledByUser}
                lastEnclosureStateRead={
                    coreState.aemet_enclosure_state.dt === null ||
                    coreState.aemet_enclosure_state.dt === undefined
                        ? null
                        : coreState.aemet_enclosure_state.dt
                }
            />
            <div className="flex flex-col flex-1 w-full overflow-y-scroll text-sm divide-y divide-blue-200 h-[calc(100vh-7.5rem)]">
                <VariableBlock
                    label="System"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Battery Voltage',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.battery_voltage,
                                    ' V'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Logger Panel Temperature',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.logger_panel_temperature,
                                    ' °C'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'AUTO mode',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.auto_mode,
                                    ''
                                ),
                            },
                            action: {
                                label: 'set auto mode',
                                callback: setAutoMode,
                                variant: 'numeric',
                                initialValue: coreState.aemet_enclosure_state.auto_mode || 0,
                            },
                        },
                        {
                            variable: {
                                key: 'ENHANCED_SECURITY mode',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.enhanced_security_mode,
                                    ''
                                ),
                            },
                            action: {
                                label: 'set enhanced security',
                                callback: setEnhancedSecurityMode,
                                variant: 'numeric',
                                initialValue:
                                    coreState.aemet_enclosure_state.enhanced_security_mode || 0,
                            },
                        },
                    ]}
                />
                <VariableBlock
                    label="Motor State"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Alert Level',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.alert_level,
                                    ''
                                ),
                            },
                            action: {
                                label: 'set alert level',
                                callback: setAlertLevel,
                                variant: 'numeric',
                                initialValue: coreState.aemet_enclosure_state.alert_level || 0,
                            },
                        },
                        {
                            variable: {
                                key: 'Averia Fault Code',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.averia_fault_code,
                                    ''
                                ),
                            },
                            action: {
                                label: 'set averia fault code',
                                callback: setAveriaFaultCode,
                                variant: 'numeric',
                                initialValue:
                                    coreState.aemet_enclosure_state.averia_fault_code || 0,
                            },
                        },
                        {
                            variable: {
                                key: 'Cover Status',
                                value: renderStringValue(
                                    (() => {
                                        const value = coreState.aemet_enclosure_state.cover_status;
                                        if (value == null) return '-';
                                        if (COVERR_STATUS_MAP[value])
                                            return COVERR_STATUS_MAP[value];
                                        return `unknown (${value})`;
                                    })(),
                                    ''
                                ),
                            },
                            action: {
                                label:
                                    coreState.aemet_enclosure_state.cover_status !== 'C'
                                        ? 'close cover'
                                        : 'open cover',
                                callback:
                                    coreState.aemet_enclosure_state.cover_status !== 'C'
                                        ? closeCover
                                        : openCover,
                            },
                        },
                        {
                            variable: {
                                key: 'Motor Position',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.motor_position,
                                    ''
                                ),
                            },
                        },
                    ]}
                />
                <VariableBlock
                    label="EM27 Power Supply"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Spectrometer Power',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state.em27_has_power
                                ),
                            },
                            action: {
                                label: coreState.aemet_enclosure_state.em27_has_power
                                    ? 'disable'
                                    : 'enable',
                                callback: togglePowerSpectrometer,
                            },
                        },
                        {
                            variable: {
                                key: 'Spectrometer Voltage',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.em27_voltage,
                                    ' V'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Spectrometer Current',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.em27_current,
                                    ' A'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Spectrometer Power',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.em27_power,
                                    ' W'
                                ),
                            },
                        },
                    ]}
                />
                <VariableBlock
                    label="Meteorological Conditions"
                    disabled={buttonsAreDisabled}
                    rows={[
                        // air pressure
                        {
                            variable: {
                                key: 'Air Pressure (internal)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.air_pressure_internal,
                                    ' hPa'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Air Pressure (external)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.air_pressure_external,
                                    ' hPa'
                                ),
                            },
                        },
                        // relative humidity
                        {
                            variable: {
                                key: 'Relative Humidity (internal)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.relative_humidity_internal,
                                    ' %'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Relative Humidity (external)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.relative_humidity_external,
                                    ' %'
                                ),
                            },
                        },

                        // air temperature
                        {
                            variable: {
                                key: 'Air Temperature (internal)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.air_temperature_internal,
                                    ' °C'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Air Temperature (external)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.air_temperature_external,
                                    ' °C'
                                ),
                            },
                        },

                        // dew point temperature
                        {
                            variable: {
                                key: 'Dew Point Temperature (internal)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.dew_point_temperature_internal,
                                    ' °C'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Dew Point Temperature (external)',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.dew_point_temperature_external,
                                    ' °C'
                                ),
                            },
                        },

                        // wind direction and speed
                        {
                            variable: {
                                key: 'Wind Direction',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.wind_direction,
                                    ' °'
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Wind Speed',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.wind_velocity,
                                    ' m/s'
                                ),
                            },
                        },

                        // rain sensor counter
                        {
                            variable: {
                                key: 'Rain Sensor 1 Counter',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.rain_sensor_counter_1,
                                    ''
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Rain Sensor 2 Counter',
                                value: renderStringValue(
                                    coreState.aemet_enclosure_state.rain_sensor_counter_2,
                                    ''
                                ),
                            },
                        },
                    ]}
                />
                <VariableBlock
                    label="Cover Opening Logic"
                    disabled={buttonsAreDisabled}
                    rows={[
                        {
                            variable: {
                                key: 'Closed due to rain',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state.closed_due_to_rain
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Closed due to external relative humidity',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state
                                        .closed_due_to_external_relative_humidity
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Closed due to internal relative humidity',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state
                                        .closed_due_to_internal_relative_humidity
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Closed due to external air temperature',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state
                                        .closed_due_to_external_air_temperature
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Closed due to internal air temperature',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state
                                        .closed_due_to_internal_air_temperature
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Closed due to wind velocity',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state.closed_due_to_wind_velocity
                                ),
                            },
                        },
                        {
                            variable: {
                                key: 'Opened due to elevated internal humidity',
                                value: renderBoolValue(
                                    coreState.aemet_enclosure_state
                                        .opened_due_to_elevated_internal_humidity
                                ),
                            },
                        },
                    ]}
                />
            </div>
        </div>
    );
}
