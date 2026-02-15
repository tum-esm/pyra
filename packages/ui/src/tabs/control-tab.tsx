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
        <div className="relative flex overflow-hidden divide-x divide-slate-300">
            <div className="flex items-center flex-shrink-0 w-48 px-4 py-2 -m-px text-base font-semibold text-gray-900 bg-slate-200">
                {props.label}
            </div>
            <div className="flex-grow py-3 pl-4 pr-3 bg-slate-50 flex-col-left gap-y-1">
                {props.rows.map((r, i) => (
                    <div className="w-full h-8 flex-row-left" key={i}>
                        <div className="flex-row-center whitespace-nowrap">
                            <div className="w-40">{r.variable.key}:</div>{' '}
                            <span className="w-12 font-semibold text-right">
                                {r.variable.value}
                            </span>
                        </div>
                        {r.action && r.variable.value !== '-' && (
                            <>
                                <div className="flex-grow" />
                                {r.action.variant === undefined && (
                                    <essentialComponents.Button
                                        variant="white"
                                        onClick={r.action.callback}
                                        key={r.action.label}
                                        className="w-52"
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
                                        className="w-52"
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
        <div className="w-full px-4 py-4 bg-white border-b flex-row-left gap-x-2 border-slate-300">
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
    const plcIsControlledByUser = centralConfig?.tum_enclosure?.controlled_by_user;

    const { commandIsRunning, runPromisingCommand } = fetchUtils.useCommand();
    const buttonsAreDisabled = !plcIsControlledByUser || commandIsRunning;

    async function setPlcIsControlledByUser(v: boolean) {
        runPromisingCommand({
            command: () =>
                fetchUtils.backend.updateConfig({ tum_enclosure: { controlled_by_user: v } }),
            label: 'toggling PLC control mode',
            successLabel: 'successfully toggled PLC control mode',
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
        <div className={'w-full relative flex-col-left'}>
            <HeaderBlock
                plcIsControlledByUser={plcIsControlledByUser || false}
                setPlcIsControlledByUser={setPlcIsControlledByUser}
                lastEnclosureStateRead={
                    coreState.tum_enclosure_state.dt === null ||
                    coreState.tum_enclosure_state.dt === undefined
                        ? null
                        : coreState.tum_enclosure_state.dt
                }
            />
            <div className="flex flex-col w-full text-sm divide-y divide-slate-300">
                <>
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
                                    value: renderBoolValue(
                                        coreState.tum_enclosure_state.state.rain
                                    ),
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
                                    value: renderBoolValue(
                                        coreState.tum_enclosure_state.power.camera
                                    ),
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
                                    value: renderBoolValue(
                                        coreState.tum_enclosure_state.power.router
                                    ),
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
                                    value: renderBoolValue(
                                        coreState.tum_enclosure_state.power.heater
                                    ),
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
                </>
            </div>
        </div>
    );
}
