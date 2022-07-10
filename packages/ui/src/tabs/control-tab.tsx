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
    variables: { key: string; value: string | number }[];
    buttonsAreDisabled: boolean;
    actions: (
        | {
              label: string;
              callback: (value: number) => void;
              spinner: boolean;
              variant: 'numeric';
              initialValue: number;
              postfix?: string;
          }
        | { label: string; callback: () => void; spinner: boolean; variant?: undefined }
    )[];
}) {
    return (
        <div className="relative flex overflow-hidden elevated-panel">
            <div className="block w-48 px-4 py-2 -m-px text-base font-semibold text-gray-900 bg-gray-100 border-r border-gray-200 rounded-l flex-row-center">
                {props.label}
            </div>
            <div className="flex-grow py-3 pl-4 pr-3 flex-row-left gap-x-4">
                <div className="flex-col-left gap-y-0.5">
                    {props.variables.map((v) => (
                        <div key={v.key} className="flex-row-center whitespace-nowrap">
                            <div className="w-40">{v.key}:</div>{' '}
                            <span className="font-semibold">{v.value}</span>
                        </div>
                    ))}
                </div>
                <div className="flex-grow flex-col-right gap-y-1">
                    {props.actions.map((a) =>
                        a.variant === undefined ? (
                            <essentialComponents.Button
                                variant="gray"
                                onClick={a.callback}
                                key={a.label}
                                spinner={a.spinner}
                                className="w-52"
                                disabled={props.buttonsAreDisabled}
                            >
                                {a.label}
                            </essentialComponents.Button>
                        ) : (
                            <essentialComponents.NumericButton
                                initialValue={a.initialValue}
                                onClick={a.callback}
                                key={a.label}
                                spinner={a.spinner}
                                className="w-52"
                                postfix={a.postfix}
                                disabled={props.buttonsAreDisabled}
                            >
                                {a.label}
                            </essentialComponents.NumericButton>
                        )
                    )}
                </div>
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

    // TODO: Improve row alignment -> align buttons and corresp. values + connecting line

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
                {pyraIsInTestMode && coreState !== undefined && (
                    <>
                        <VariableBlock
                            label="Errors"
                            buttonsAreDisabled={buttonsAreDisabled}
                            variables={[
                                {
                                    key: 'Reset needed',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.state.reset_needed
                                    ),
                                },
                                {
                                    key: 'Motor failed',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.state.motor_failed
                                    ),
                                },
                                {
                                    key: 'UPS alert',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.state.ups_alert
                                    ),
                                },
                            ]}
                            actions={[
                                { label: 'reset now', callback: reset, spinner: isLoadingReset },
                            ]}
                        />
                        <VariableBlock
                            label="Rain Detection"
                            buttonsAreDisabled={buttonsAreDisabled}
                            variables={[
                                {
                                    key: 'Cover is closed',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.state.cover_closed
                                    ),
                                },
                                {
                                    key: 'Rain detected',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.state.rain
                                    ),
                                },
                            ]}
                            actions={[
                                {
                                    label: 'force cover close',
                                    callback: closeCover,
                                    spinner: isLoadingCloseCover,
                                },
                            ]}
                        />
                        <VariableBlock
                            label="Cover Angle"
                            buttonsAreDisabled={buttonsAreDisabled}
                            variables={[
                                {
                                    key: 'Current cover angle',
                                    value: renderStringValue(
                                        coreState.enclosure_plc_readings.actors.current_angle,
                                        '°'
                                    ),
                                },
                                {
                                    key: 'Sync to CamTracker',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.control.sync_to_tracker
                                    ),
                                },
                            ]}
                            actions={[
                                {
                                    label: 'move to angle',
                                    callback: moveCover,
                                    spinner: isLoadingMoveCover,
                                    variant: 'numeric',
                                    initialValue:
                                        coreState.enclosure_plc_readings.actors.current_angle || 0,
                                    postfix: '°',
                                },
                                {
                                    label: coreState.enclosure_plc_readings.control.sync_to_tracker
                                        ? 'do not sync to tracker'
                                        : 'sync to tracker',
                                    callback: toggleSyncToTracker,
                                    spinner: isLoadingSyncTotracker,
                                },
                            ]}
                        />
                        <VariableBlock
                            label="Climate"
                            buttonsAreDisabled={buttonsAreDisabled}
                            variables={[
                                {
                                    key: 'Temperature',
                                    value: renderStringValue(
                                        coreState.enclosure_plc_readings.sensors.temperature,
                                        ' °C'
                                    ),
                                },
                                {
                                    key: 'Humidity',
                                    value: renderStringValue(
                                        coreState.enclosure_plc_readings.sensors.humidity,
                                        '%'
                                    ),
                                },
                                {
                                    key: 'Fan Speed',
                                    value: renderStringValue(
                                        coreState.enclosure_plc_readings.actors.fan_speed,
                                        '%'
                                    ),
                                },
                                {
                                    key: 'Auto temperature',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.control.auto_temp_mode
                                    ),
                                },
                            ]}
                            actions={[
                                {
                                    label: coreState.enclosure_plc_readings.control.auto_temp_mode
                                        ? 'disable auto temperature'
                                        : 'enable auto temperature',
                                    callback: toggleAutoTemperature,
                                    spinner: isLoadingAutoTemperature,
                                },
                            ]}
                        />
                        <VariableBlock
                            label="Power"
                            buttonsAreDisabled={buttonsAreDisabled}
                            variables={[
                                {
                                    key: 'Camera Power',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.power.camera
                                    ),
                                },
                                {
                                    key: 'Router Power',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.power.router
                                    ),
                                },
                                {
                                    key: 'Spectrometer Power',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.power.spectrometer
                                    ),
                                },
                                {
                                    key: 'Computer Power',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.power.computer
                                    ),
                                },
                                {
                                    key: 'Heater power',
                                    value: renderBoolValue(
                                        coreState.enclosure_plc_readings.power.heater
                                    ),
                                },
                            ]}
                            actions={[
                                {
                                    label: coreState.enclosure_plc_readings.power.camera
                                        ? 'disable camera power'
                                        : 'enable camera power',
                                    callback: togglePowerCamera,
                                    spinner: isLoadingPowerCamera,
                                },
                                {
                                    label: coreState.enclosure_plc_readings.power.router
                                        ? 'disable router power'
                                        : 'enable router power',
                                    callback: togglePowerRouter,
                                    spinner: isLoadingPowerRouter,
                                },
                                {
                                    label: coreState.enclosure_plc_readings.power.spectrometer
                                        ? 'disable spectrometer power'
                                        : 'enable spectrometer power',
                                    callback: togglePowerSpectrometer,
                                    spinner: isLoadingPowerSpectrometer,
                                },
                                {
                                    label: coreState.enclosure_plc_readings.power.computer
                                        ? 'disable computer power'
                                        : 'enable computer power',
                                    callback: togglePowerComputer,
                                    spinner: isLoadingPowerComputer,
                                },
                                {
                                    label: coreState.enclosure_plc_readings.power.heater
                                        ? 'disable heater power'
                                        : 'enable heater power',
                                    callback: togglePowerHeater,
                                    spinner: isLoadingPowerHeater,
                                },
                            ]}
                        />
                    </>
                )}
            </div>
        </div>
    );
}
