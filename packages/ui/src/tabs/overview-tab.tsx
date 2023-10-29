import { fetchUtils } from '../utils';
import { essentialComponents, overviewComponents } from '../components';
import ICONS from '../assets/icons';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { mean } from 'lodash';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import { useCoreStateStore } from '../utils/zustand-utils/core-state-zustand';
import { ChildProcess } from '@tauri-apps/api/shell';

function SystemRow(props: { label: string; value: React.ReactNode }) {
    return (
        <div className="w-full pl-2 flex-row-left">
            <div className="w-32">{props.label}:</div>
            <div className="min-w-[2rem]">{props.value}</div>
        </div>
    );
}

export default function OverviewTab() {
    const { coreState } = useCoreStateStore();
    const [isLoadingCloseCover, setIsLoadingCloseCover] = useState(false);

    const { mainLogs } = useLogsStore();
    const currentInfoLogLines = mainLogs?.slice(-15);

    async function closeCover() {
        toast.promise(fetchUtils.backend.writeToPLC(['close-cover']), {
            loading: 'Closing cover ...',
            success: (result: ChildProcess) =>
                `Successfully closed cover: ${JSON.stringify(result)}`,
            error: (result: ChildProcess) =>
                `Could not write to PLC - processResults = ${JSON.stringify(result)}`,
        });
    }

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
        <div className={'flex-col-center w-full pb-4 relative overflow-x-hidden bg-slate-50'}>
            <overviewComponents.PyraCoreStatus />
            <div className="w-full px-4 py-4 pb-0 text-base font-semibold">Today's Activity</div>
            <div className="w-full p-4 pt-0">
                <overviewComponents.ActivityPlot />
            </div>
            <div className="w-full px-4 py-4 pb-2 text-base font-semibold border-t border-slate-200">
                System Status
            </div>
            {coreState === undefined && (
                <div className="w-full p-4 text-sm flex-row-left gap-x-2">
                    State is loading <essentialComponents.Spinner />
                </div>
            )}
            {coreState?.plc_state.state.rain === true &&
                coreState?.plc_state.state.cover_closed === false && (
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
                            value={renderString(coreState.plc_state.sensors.temperature, {
                                appendix: '°C',
                            })}
                        />
                        <SystemRow
                            label="Reset needed"
                            value={renderBoolean(coreState.plc_state.state.reset_needed)}
                        />
                        <SystemRow
                            label="Motor failed"
                            value={renderBoolean(coreState.plc_state.state.motor_failed)}
                        />
                        <SystemRow
                            label="Cover is closed"
                            value={renderBoolean(coreState.plc_state.state.cover_closed)}
                        />
                        <SystemRow
                            label="Rain detected"
                            value={renderBoolean(coreState.plc_state.state.rain)}
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
                            value={renderString(coreState.operating_system_state.last_boot_time)}
                        />
                        <SystemRow
                            label="Disk space usage"
                            value={renderSystemBar(
                                coreState.operating_system_state.filled_disk_space_fraction
                            )}
                        />
                        <SystemRow
                            label="CPU usage"
                            value={renderSystemBar(coreState.operating_system_state.cpu_usage)}
                        />
                        <SystemRow
                            label="Memory usage"
                            value={renderSystemBar(coreState.operating_system_state.memory_usage)}
                        />
                    </div>
                </div>
            )}
            <div className="w-full px-4 py-4 pb-0 text-base font-semibold border-t border-slate-200">
                Measurement Decision
            </div>
            <div className="w-full p-4 pt-2 text-sm flex-row-left gap-x-1">
                <overviewComponents.MeasurementDecision />
            </div>
            <div className="w-full px-4 pt-3 pb-2 text-base font-semibold border-t border-slate-200">
                Recent Log Lines
            </div>
            <div className="w-[calc(100%-2rem)] mx-4 rounded-lg overflow-hidden font-mono text-xs bg-white border border-slate-200 py-1">
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
