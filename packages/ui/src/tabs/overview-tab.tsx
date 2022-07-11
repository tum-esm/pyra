import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import ICONS from '../assets/icons';
import { useState } from 'react';
import { customTypes } from '../custom-types';
import toast from 'react-hot-toast';

export default function OverviewTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.body);
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    const measurementDecision = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_decision
    );
    const automaticMeasurementDecisionResult = reduxUtils.useTypedSelector(
        (s) => s.coreState.body?.measurements_should_be_running
    );
    let measurementDecisionResult: boolean | undefined = undefined;
    switch (measurementDecision?.mode) {
        case 'manual':
            measurementDecisionResult = measurementDecision.manual_decision_result;
            break;
        case 'cli':
            measurementDecisionResult = measurementDecision.cli_decision_result;
            break;
        case 'automatic':
            measurementDecisionResult = automaticMeasurementDecisionResult;
            break;
    }

    const [isLoadingCloseCover, setIsLoadingCloseCover] = useState(false);
    const dispatch = reduxUtils.useTypedDispatch();
    const setCoreStatePartial = (c: customTypes.partialCoreState) =>
        dispatch(reduxUtils.coreStateActions.setPartial(c));

    // reused function from control-tab
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

    // reused function from control-tab
    async function closeCover() {
        await runPlcWriteCommand(['close-cover'], setIsLoadingCloseCover, {
            state: { cover_closed: true },
            actors: { current_angle: 0 },
        });
    }

    const allInfoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
    const currentInfoLogLines = allInfoLogLines?.slice(-10);

    function renderStateValue(
        value: null | boolean | number | string | number[],
        options: { trueLabel: string; falseLabel: string; numberAppendix: string }
    ) {
        if (value === null) {
            return '-';
        }
        if (typeof value === 'boolean') {
            return value ? options.trueLabel : options.falseLabel;
        }
        if (typeof value === 'string') {
            return value;
        }
        if (typeof value === 'object') {
            return value.map((v) => `${v}%`).join(' | ');
        }
        return `${value} ${options.numberAppendix}`;
    }

    return (
        <div className={'flex-col-center w-full h-full overflow-y-scroll gap-y-4 pt-4 pb-12 px-6'}>
            <div className="w-full text-sm h-7 flex-row-left">
                <essentialComponents.Ping state={true} />
                <span className="ml-2.5 mr-1">
                    pyra-core is running with process ID {pyraCorePID}
                </span>
            </div>
            <div className="w-full -mt-2 text-sm font-normal flex-row-left">
                <essentialComponents.Ping state={measurementDecisionResult} />
                <span className="ml-2.5 mr-1">Measurements are currently</span>
                {measurementDecisionResult === undefined && <essentialComponents.Spinner />}
                {!(measurementDecisionResult === undefined) && (
                    <>
                        {!measurementDecisionResult && <>not running</>}
                        {measurementDecisionResult && <>running</>}
                    </>
                )}
                {measurementDecision?.mode !== undefined && (
                    <strong className="ml-1 font-semibold">
                        ({measurementDecision.mode} mode)
                    </strong>
                )}
            </div>
            <div className="w-full h-px bg-gray-300" />
            {coreState === undefined && (
                <div className="w-full flex-row-left gap-x-2">
                    State is loading <essentialComponents.Spinner />
                </div>
            )}
            {coreState?.enclosure_plc_readings.state.rain === true &&
                coreState?.enclosure_plc_readings.state.cover_closed === false && (
                    <div
                        className={
                            'w-full py-1 pl-2 pr-3 flex-row-left gap-x-1 shadow-sm ' +
                            'bg-red-600 rounded-md text-red-50 text-sm font-semibold ' +
                            'border border-red-900 -mb-2 '
                        }
                    >
                        <div className="w-6 h-6 p-[0.075rem] text-white">{ICONS.alert}</div>
                        Rain was detected but cover is not closed!
                    </div>
                )}
            {coreState !== undefined && (
                <div className="flex flex-row items-start justify-start w-full">
                    <div
                        className={
                            'flex-col items-start justify-start pr-3 text-sm gap-y-1 h-full ' +
                            'border-r border-gray-300 min-w-[16rem]'
                        }
                    >
                        {[
                            {
                                label: 'Temperature',
                                value: coreState.enclosure_plc_readings.sensors.temperature,
                            },
                            {
                                label: 'Reset needed',
                                value: coreState.enclosure_plc_readings.state.reset_needed,
                            },
                            {
                                label: 'Motor failed',
                                value: coreState.enclosure_plc_readings.state.motor_failed,
                            },
                            {
                                label: 'Cover is closed',
                                value: coreState.enclosure_plc_readings.state.cover_closed,
                            },
                            {
                                label: 'Rain Detected',
                                value: coreState.enclosure_plc_readings.state.rain,
                            },
                        ].map((s) => (
                            <div className="w-full pl-2 flex-row-left">
                                <div className="w-32">{s.label}:</div>
                                <div className="min-w-[2rem]">
                                    {renderStateValue(s.value, {
                                        trueLabel: 'Yes',
                                        falseLabel: 'No',
                                        numberAppendix: '°C',
                                    })}
                                </div>
                            </div>
                        ))}
                        <essentialComponents.Button
                            variant="red"
                            onClick={closeCover}
                            className="w-full mt-1.5"
                            spinner={isLoadingCloseCover}
                        >
                            force cover close
                        </essentialComponents.Button>
                    </div>
                    <div className="flex-col items-start justify-start pl-3 text-sm">
                        {[
                            {
                                label: 'Last boot time',
                                value: coreState.os_state.last_boot_time,
                            },
                            {
                                label: 'Disk space usage',
                                value: coreState.os_state.filled_disk_space_fraction,
                            },
                            {
                                label: 'CPU cores usage',
                                value: coreState.os_state.cpu_usage,
                            },
                            {
                                label: 'Memory usage',
                                value: coreState.os_state.memory_usage,
                            },
                        ].map((s) => (
                            <div className="w-full flex-row-left">
                                <div className="w-32">{s.label}:</div>
                                <div>
                                    {renderStateValue(s.value, {
                                        trueLabel: 'Yes',
                                        falseLabel: 'No',
                                        numberAppendix: '%',
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            <div className="w-full h-px bg-gray-300" />
            <div className="w-full pl-2 -mb-1 text-sm font-medium">Last 10 log lines:</div>
            <div
                className={
                    'w-full !mb-0 bg-white flex-grow text-xs ' +
                    'border border-gray-250 shadow-sm rounded-md -mt-2 ' +
                    'font-mono overflow-hidden'
                }
            >
                {currentInfoLogLines === undefined && <essentialComponents.Spinner />}
                {currentInfoLogLines !== undefined &&
                    currentInfoLogLines.map((l, i) => (
                        <essentialComponents.LogLine key={`${i} ${l}`} text={l} />
                    ))}
            </div>
        </div>
    );
}
