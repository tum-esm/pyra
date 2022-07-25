import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import { useState } from 'react';
import { customTypes } from '../custom-types';
import { ICONS } from '../assets';
import toast from 'react-hot-toast';

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
                  spinner: boolean;
                  variant: 'numeric';
                  initialValue: number;
                  postfix?: string;
              }
            | { label: string; callback: () => void; spinner: boolean; variant?: undefined };
    }[];
}) {
    return (
        <div className="relative flex overflow-hidden elevated-panel">
            <div className="block w-48 px-4 py-2 -m-px text-base font-semibold text-gray-900 bg-gray-100 border-r border-gray-200 rounded-l flex-row-center">
                {props.label}
            </div>
            <div className="flex-grow py-3 pl-4 pr-3 flex-col-left gap-y-1">
                {props.rows.map((r, i) => (
                    <div className="w-full flex-row-left h-7" key={i}>
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
                                        variant="gray"
                                        onClick={r.action.callback}
                                        key={r.action.label}
                                        spinner={r.action.spinner}
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
                                        spinner={r.action.spinner}
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
export default function ControlTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.body);
    const plcIsControlledByUser = reduxUtils.useTypedSelector(
        (s) => s.config.central?.tum_plc?.controlled_by_user
    );
    const pyraIsInTestMode = reduxUtils.useTypedSelector(
        (s) => s.config.central?.general.test_mode
    );

    const dispatch = reduxUtils.useTypedDispatch();
    const setConfigsPartial = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setConfigsPartial(c));

    const setCoreStatePartial = (c: customTypes.partialCoreState) =>
        dispatch(reduxUtils.coreStateActions.setPartial(c));

    const [isLoadingManualToggle, setIsLoadingManualToggle] = useState(false);
    const [isLoadingReset, setIsLoadingReset] = useState(false);
    const [isLoadingCloseCover, setIsLoadingCloseCover] = useState(false);
    const [isLoadingMoveCover, setIsLoadingMoveCover] = useState(false);
    const [isLoadingSyncTotracker, setIsLoadingSyncTotracker] = useState(false);
    const [isLoadingAutoTemperature, setIsLoadingAutoTemperature] = useState(false);

    const [isLoadingPowerHeater, setIsLoadingPowerHeater] = useState(false);
    const [isLoadingPowerCamera, setIsLoadingPowerCamera] = useState(false);
    const [isLoadingPowerRouter, setIsLoadingPowerRouter] = useState(false);
    const [isLoadingPowerSpectrometer, setIsLoadingPowerSpectrometer] = useState(false);
    const [isLoadingPowerComputer, setIsLoadingPowerComputer] = useState(false);

    const buttonsAreDisabled =
        !plcIsControlledByUser ||
        isLoadingManualToggle ||
        isLoadingReset ||
        isLoadingCloseCover ||
        isLoadingMoveCover ||
        isLoadingSyncTotracker ||
        isLoadingAutoTemperature ||
        isLoadingPowerHeater ||
        isLoadingPowerCamera ||
        isLoadingPowerRouter ||
        isLoadingPowerSpectrometer ||
        isLoadingPowerComputer;

    async function setPlcIsControlledByUser(v: boolean) {
        setIsLoadingManualToggle(true);
        const update = { tum_plc: { controlled_by_user: v } };
        let result = await fetchUtils.backend.updateConfig(update);
        if (!result.stdout.includes('Updated config file')) {
            console.error(
                `Could not update config file. processResult = ${JSON.stringify(result)}`
            );
            toast.error(`Could not update config file, please look in the console for details`);
        } else {
            setConfigsPartial(update);
        }
        setIsLoadingManualToggle(false);
    }

    async function runPlcWriteCommand(
        command: string[],
        setLoading: (l: boolean) => void,
        stateUpdateIfSuccessful: customTypes.partialEnclosurePlcReadings
    ) {
        setLoading(true);
        const result = await fetchUtils.backend.writeToPLC(command);
        if (result.stdout.replace(/[\n\s]*/g, '') !== 'Ok') {
            if (result.code === 0) {
                toast.error(`Could not write to PLC: ${result.stdout}`);
            } else {
                toast.error('Could not write to PLC - details in console');
                console.error(`Could not write to PLC, processResults = ${JSON.stringify(result)}`);
            }
            setLoading(false);
            throw '';
        } else {
            setCoreStatePartial({ enclosure_plc_readings: stateUpdateIfSuccessful });
            setLoading(false);
        }
    }

    async function reset() {
        await runPlcWriteCommand(['reset'], setIsLoadingReset, {
            state: { reset_needed: false },
        });
    }

    async function closeCover() {
        await runPlcWriteCommand(['close-cover'], setIsLoadingCloseCover, {
            state: { cover_closed: true },
            actors: { current_angle: 0 },
        });
    }

    async function moveCover(angle: number) {
        if (angle === 0 || (angle >= 110 && angle <= 250)) {
            await runPlcWriteCommand(['set-cover-angle', angle.toString()], setIsLoadingMoveCover, {
                state: { cover_closed: angle === 0 },
                actors: { current_angle: angle },
            });
        } else {
            toast.error(`Angle has to be either 0 or between 110° and 250°`);
        }
    }

    async function toggleSyncToTracker() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.control.sync_to_tracker;
            await runPlcWriteCommand(
                ['set-sync-to-tracker', JSON.stringify(newValue)],
                setIsLoadingSyncTotracker,
                {
                    control: { sync_to_tracker: newValue },
                }
            );
        }
    }

    async function toggleAutoTemperature() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.control.auto_temp_mode;
            await runPlcWriteCommand(
                ['set-auto-temperature', JSON.stringify(newValue)],
                setIsLoadingAutoTemperature,
                {
                    control: { auto_temp_mode: newValue },
                }
            );
        }
    }

    async function togglePowerHeater() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.power.heater;
            await runPlcWriteCommand(
                ['set-heater-power', JSON.stringify(newValue)],
                setIsLoadingPowerHeater,
                {
                    power: { heater: newValue },
                }
            );
        }
    }

    async function togglePowerCamera() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.power.camera;
            await runPlcWriteCommand(
                ['set-camera-power', JSON.stringify(newValue)],
                setIsLoadingPowerCamera,
                {
                    power: { camera: newValue },
                }
            );
        }
    }

    async function togglePowerRouter() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.power.router;
            await runPlcWriteCommand(
                ['set-router-power', JSON.stringify(newValue)],
                setIsLoadingPowerRouter,
                {
                    power: { router: newValue },
                }
            );
        }
    }

    async function togglePowerSpectrometer() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.power.spectrometer;
            await runPlcWriteCommand(
                ['set-spectrometer-power', JSON.stringify(newValue)],
                setIsLoadingPowerSpectrometer,
                {
                    power: { spectrometer: newValue },
                }
            );
        }
    }

    async function togglePowerComputer() {
        if (coreState !== undefined) {
            const newValue = !coreState.enclosure_plc_readings.power.computer;
            await runPlcWriteCommand(
                ['set-computer-power', JSON.stringify(newValue)],
                setIsLoadingPowerComputer,
                {
                    power: { computer: newValue },
                }
            );
        }
    }

    if (plcIsControlledByUser === undefined) {
        return <></>;
    }

    return (
        <div className={'w-full relative px-6 py-6 flex-col-left gap-y-4'}>
            <div className="flex-row-left gap-x-2">
                <div>PLC is controlled by:</div>
                <essentialComponents.Toggle
                    value={plcIsControlledByUser ? 'user' : 'automation'}
                    values={['user', 'automation']}
                    setValue={(v) => setPlcIsControlledByUser(v === 'user')}
                />
                {isLoadingManualToggle && <essentialComponents.Spinner />}
                {!isLoadingManualToggle && (
                    <div className="text-sm text-gray-500 flex-row-center">
                        <div className="w-4 h-4 mr-1">{ICONS.info}</div>
                        {plcIsControlledByUser && 'The automation will skip all PLC related logic'}
                        {!plcIsControlledByUser && 'You cannot send any commands to the PLC'}
                    </div>
                )}
            </div>
            <div className="w-full h-px my-0 bg-gray-300" />
            <div className="flex flex-col w-full text-sm gap-y-2">
                {pyraIsInTestMode && (
                    <div className="flex-row-center">
                        No PLC connection when pyra is in test mode
                    </div>
                )}
                {!pyraIsInTestMode && coreState === undefined && (
                    <div className="flex-row-center gap-x-1.5">
                        <essentialComponents.Spinner />
                        loading PLC state
                    </div>
                )}
                {!pyraIsInTestMode && coreState !== undefined && (
                    <>
                        <VariableBlock
                            label="Errors"
                            disabled={buttonsAreDisabled}
                            rows={[
                                {
                                    variable: {
                                        key: 'Reset needed',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.state.reset_needed
                                        ),
                                    },
                                    action: {
                                        label: 'reset now',
                                        callback: reset,
                                        spinner: isLoadingReset,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Motor failed',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.state.motor_failed
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'UPS alert',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.state.ups_alert
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
                                            coreState.enclosure_plc_readings.state.cover_closed
                                        ),
                                    },
                                    action: {
                                        label: 'force cover close',
                                        callback: closeCover,
                                        spinner: isLoadingCloseCover,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Rain detected',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.state.rain
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
                                            coreState.enclosure_plc_readings.actors.current_angle,
                                            '°'
                                        ),
                                    },
                                    action: {
                                        label: 'move to angle',
                                        callback: moveCover,
                                        spinner: isLoadingMoveCover,
                                        variant: 'numeric',
                                        initialValue:
                                            coreState.enclosure_plc_readings.actors.current_angle ||
                                            0,
                                        postfix: '°',
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Sync to CamTracker',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.control.sync_to_tracker
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.control
                                            .sync_to_tracker
                                            ? 'do not sync'
                                            : 'sync',
                                        callback: toggleSyncToTracker,
                                        spinner: isLoadingSyncTotracker,
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
                                            coreState.enclosure_plc_readings.sensors.temperature,
                                            ' °C'
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Humidity',
                                        value: renderStringValue(
                                            coreState.enclosure_plc_readings.sensors.humidity,
                                            '%'
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Fan Speed',
                                        value: renderStringValue(
                                            coreState.enclosure_plc_readings.actors.fan_speed,
                                            '%'
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Auto temperature',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.control.auto_temp_mode
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.control
                                            .auto_temp_mode
                                            ? 'disable'
                                            : 'enable',
                                        callback: toggleAutoTemperature,
                                        spinner: isLoadingAutoTemperature,
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
                                            coreState.enclosure_plc_readings.power.camera
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.power.camera
                                            ? 'disable'
                                            : 'enable',
                                        callback: togglePowerCamera,
                                        spinner: isLoadingPowerCamera,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Router Power',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.power.router
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.power.router
                                            ? 'disable'
                                            : 'enable',
                                        callback: togglePowerRouter,
                                        spinner: isLoadingPowerRouter,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Spectrometer Power',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.power.spectrometer
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.power.spectrometer
                                            ? 'disable'
                                            : 'enable',
                                        callback: togglePowerSpectrometer,
                                        spinner: isLoadingPowerSpectrometer,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Computer Power',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.power.computer
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.power.computer
                                            ? 'disable'
                                            : 'enable',
                                        callback: togglePowerComputer,
                                        spinner: isLoadingPowerComputer,
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Heater power',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.power.heater
                                        ),
                                    },
                                    action: {
                                        label: coreState.enclosure_plc_readings.power.heater
                                            ? 'disable'
                                            : 'enable',
                                        callback: togglePowerHeater,
                                        spinner: isLoadingPowerHeater,
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
                                            coreState.enclosure_plc_readings.connections.camera
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Computer',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.connections.computer
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Heater',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.connections.heater
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Router',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.connections.router
                                        ),
                                    },
                                },
                                {
                                    variable: {
                                        key: 'Spectrometer',
                                        value: renderBoolValue(
                                            coreState.enclosure_plc_readings.connections
                                                .spectrometer
                                        ),
                                    },
                                },
                            ]}
                        />
                    </>
                )}
            </div>
        </div>
    );
}
