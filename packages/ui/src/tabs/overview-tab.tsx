import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents, overviewComponents } from '../components';
import ICONS from '../assets/icons';
import { useState } from 'react';
import { customTypes } from '../custom-types';
import toast from 'react-hot-toast';
import { mean } from 'lodash';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import { IconActivityHeartbeat, IconCpu, IconTimelineEventText } from '@tabler/icons-react';
import PyraCoreStatus from '../components/automation/pyra-core-status';

function SystemRow(props: { label: string; value: React.ReactNode }) {
    return (
        <div className="w-full pl-2 flex-row-left">
            <div className="w-32">{props.label}:</div>
            <div className="min-w-[2rem]">{props.value}</div>
        </div>
    );
}

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

    const { mainLogs } = useLogsStore();
    const currentInfoLogLines = mainLogs?.slice(-15);

    function renderSystemBar(value: null | number | number[]) {
        if (value === null) {
            return '-';
        }
        if (typeof value === 'object') {
            value = mean(value);
        }
        return (
            <div className="flex-row-center">
                <div className="relative w-32 h-2 overflow-hidden bg-white border rounded-full border-gray-250">
                    <div
                        className="h-full bg-slate-700"
                        style={{ width: `${value.toFixed(3)}%` }}
                    />
                </div>
                <div className="ml-1.5 font-mono w-[3.375rem] text-right">{value.toFixed(1)} %</div>
            </div>
        );
    }

    function renderString(value: null | string | number, options?: { appendix: string }) {
        if (value === null) {
            return '-';
        } else {
            return `${value}${options !== undefined ? options.appendix : ''}`;
        }
    }

    function renderBoolean(value: null | boolean) {
        if (value === null) {
            return '-';
        } else {
            return value ? 'Yes' : 'No';
        }
    }

    return (
        <div className={'flex-col-center w-full pb-4 relative overflow-x-hidden bg-white'}>
            <div className="flex flex-row items-center justify-start w-full px-4 py-2 text-base font-medium text-white bg-gray-800 gap-x-3">
                <IconActivityHeartbeat size={20} className="text-gray-200" /> Pyra Core
            </div>

            <PyraCoreStatus />
            <div className="w-full p-4 text-sm border-t border-gray-200 flex-row-left gap-x-1">
                <essentialComponents.Ping state={measurementDecisionResult} />
                <span className="ml-1">Measurements are currently</span>
                {measurementDecisionResult === undefined && <essentialComponents.Spinner />}
                {!(measurementDecisionResult === undefined) && (
                    <>
                        {!measurementDecisionResult && <>not running</>}
                        {measurementDecisionResult && <>running</>}
                    </>
                )}
            </div>
            <div className="w-full p-4 pt-2 border-t border-gray-200">
                <overviewComponents.ActivityPlot />
            </div>
            <div className="flex flex-row items-center justify-start w-full px-4 py-2 text-base font-medium text-white bg-gray-800 gap-x-3">
                <IconCpu size={20} className="text-gray-200" /> System State
            </div>
            {coreState === undefined && (
                <div className="w-full p-4 text-sm bg-white flex-row-left gap-x-2">
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
                <div className="grid w-full grid-cols-2">
                    <div
                        className={
                            'flex-col items-start justify-start pr-3 text-sm gap-y-1 ' +
                            'border-r border-gray-300 min-w-[16rem]'
                        }
                    >
                        <SystemRow
                            label="Temperature"
                            value={renderString(
                                coreState.enclosure_plc_readings.sensors.temperature,
                                { appendix: '°C' }
                            )}
                        />
                        <SystemRow
                            label="Reset needed"
                            value={renderBoolean(
                                coreState.enclosure_plc_readings.state.reset_needed
                            )}
                        />
                        <SystemRow
                            label="Motor failed"
                            value={renderBoolean(
                                coreState.enclosure_plc_readings.state.motor_failed
                            )}
                        />
                        <SystemRow
                            label="Cover is closed"
                            value={renderBoolean(
                                coreState.enclosure_plc_readings.state.cover_closed
                            )}
                        />
                        <SystemRow
                            label="Rain detected"
                            value={renderBoolean(coreState.enclosure_plc_readings.state.rain)}
                        />
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
                        <SystemRow
                            label="Last boot time"
                            value={renderString(coreState.os_state.last_boot_time)}
                        />
                        <SystemRow
                            label="Disk space usage"
                            value={renderSystemBar(coreState.os_state.filled_disk_space_fraction)}
                        />
                        <SystemRow
                            label="CPU usage"
                            value={renderSystemBar(coreState.os_state.cpu_usage)}
                        />
                        <SystemRow
                            label="Memory usage"
                            value={renderSystemBar(coreState.os_state.memory_usage)}
                        />
                    </div>
                </div>
            )}

            <div className="flex flex-row items-center justify-start w-full px-4 py-2 text-base font-medium text-white bg-gray-800 gap-x-3">
                <IconTimelineEventText size={20} className="text-gray-200" /> Recent Log Lines
            </div>
            <div className="w-full overflow-hidden font-mono text-xs bg-white">
                {(currentInfoLogLines === undefined || currentInfoLogLines.length === 0) && (
                    <div className="p-2">
                        <essentialComponents.Spinner />
                    </div>
                )}
                {currentInfoLogLines !== undefined &&
                    currentInfoLogLines.map((l, i) => (
                        <essentialComponents.LogLine key={`${i} ${l}`} text={l} />
                    ))}
            </div>
        </div>
    );
}
