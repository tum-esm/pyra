import { fetchUtils } from '../utils';
import { essentialComponents, overviewComponents } from '../components';
import ICONS from '../assets/icons';
import { mean } from 'lodash';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import { useCoreStateStore } from '../utils/zustand-utils/core-state-zustand';
import { useConfigStore } from '../utils/zustand-utils/config-zustand';
import { Button } from '../components/ui/button';
import { IconCloudRain } from '@tabler/icons-react';

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
    const { mainLogs } = useLogsStore();
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { centralConfig } = useConfigStore();

    async function closeCover() {
        runPromisingCommand({
            command: () => fetchUtils.backend.writeToPLC(['close-cover']),
            label: 'closing cover',
            successLabel: 'successfully closed cover',
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
                Computer Status
            </div>
            <div className="grid w-full grid-cols-4 px-4 pb-4 text-sm gap-x-1">
                <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                    <div className="text-xs font-semibold">Last Boot Time</div>
                    <div>{coreState?.operating_system_state.last_boot_time}</div>
                </div>
                <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                    <div className="text-xs font-semibold">Disk Usage</div>
                    <div className="flex flex-row items-center justify-center gap-x-2">
                        {coreState?.operating_system_state.filled_disk_space_fraction ? (
                            <>
                                <div className="min-w-12 whitespace-nowrap">
                                    {coreState.operating_system_state.filled_disk_space_fraction.toFixed(
                                        1
                                    ) + ' %'}
                                </div>
                                <div className="relative flex-grow h-2 overflow-hidden rounded-full bg-slate-200">
                                    <div
                                        className="absolute top-0 bottom-0 left-0 bg-slate-500"
                                        style={{
                                            width: `${coreState.operating_system_state.filled_disk_space_fraction}%`,
                                        }}
                                    />
                                </div>
                            </>
                        ) : (
                            '-'
                        )}
                    </div>
                </div>
                <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                    <div className="text-xs font-semibold">CPU Usage</div>
                    <div className="flex flex-row items-center justify-center gap-x-2">
                        {coreState?.operating_system_state.cpu_usage ? (
                            <>
                                <div className="min-w-12 whitespace-nowrap">
                                    {mean(coreState.operating_system_state.cpu_usage).toFixed(1) +
                                        ' %'}
                                </div>
                                <div className="relative flex-grow h-2 overflow-hidden rounded-full bg-slate-200">
                                    <div
                                        className="absolute top-0 bottom-0 left-0 bg-slate-500"
                                        style={{
                                            width: `${mean(
                                                coreState.operating_system_state.cpu_usage
                                            )}%`,
                                        }}
                                    />
                                </div>
                            </>
                        ) : (
                            '-'
                        )}
                    </div>
                </div>
                <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                    <div className="text-xs font-semibold">Memory Usage</div>
                    <div className="flex flex-row items-center justify-center gap-x-2">
                        {coreState?.operating_system_state.memory_usage ? (
                            <>
                                <div className="min-w-12 whitespace-nowrap">
                                    {coreState.operating_system_state.memory_usage.toFixed(1) +
                                        ' %'}
                                </div>
                                <div className="relative flex-grow h-2 overflow-hidden rounded-full bg-slate-200">
                                    <div
                                        className="absolute top-0 bottom-0 left-0 bg-slate-500"
                                        style={{
                                            width: `${coreState.operating_system_state.memory_usage}%`,
                                        }}
                                    />
                                </div>
                            </>
                        ) : (
                            '-'
                        )}
                    </div>
                </div>
            </div>
            {centralConfig?.tum_plc && coreState && (
                <>
                    <div className="flex flex-row items-center w-full px-4 py-4 pb-2 text-base font-semibold border-t border-slate-200">
                        <div>TUM Enclosure Status</div>
                        <div className="flex-grow" />
                        <Button onClick={closeCover} className="mt-1.5">
                            force cover close
                        </Button>
                    </div>
                    <div className="grid w-full grid-cols-5 px-4 pb-4 text-sm gap-x-1">
                        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                            <div className="text-xs font-semibold">Cover Angle</div>
                            <div>
                                {coreState?.plc_state.actors.current_angle === null
                                    ? '-'
                                    : `${coreState?.plc_state.actors.current_angle} °`}
                            </div>
                        </div>
                        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                            <div className="text-xs font-semibold">Enclosure Temperature</div>
                            <div>
                                {coreState.plc_state.sensors.temperature === null
                                    ? '-'
                                    : `${coreState?.plc_state.sensors.temperature} °C`}
                            </div>
                        </div>
                        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                            <div className="text-xs font-semibold">Reset Needed</div>
                            <div>
                                {coreState.plc_state.state.reset_needed === null
                                    ? '-'
                                    : coreState.plc_state.state.reset_needed
                                    ? 'yes'
                                    : 'no'}
                            </div>
                        </div>
                        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                            <div className="text-xs font-semibold">Motor Failed</div>
                            <div>
                                {coreState.plc_state.state.motor_failed === null
                                    ? '-'
                                    : coreState.plc_state.state.motor_failed
                                    ? 'yes'
                                    : 'no'}
                            </div>
                        </div>
                        <div className="flex flex-col p-2 bg-white border rounded-md shadow-sm border-slate-200 gap-y-1">
                            <div className="text-xs font-semibold">Rain Detected</div>
                            <div>
                                {coreState.plc_state.state.rain === null
                                    ? '-'
                                    : coreState.plc_state.state.rain
                                    ? 'yes'
                                    : 'no'}
                            </div>
                        </div>
                    </div>
                    {coreState?.plc_state.state.rain === true &&
                        coreState?.plc_state.state.cover_closed === false && (
                            <div className="w-full px-4 mb-4 -mt-2 text-sm">
                                <div
                                    className={
                                        'flex w-full flex-row items-center flex-grow p-3 font-medium rounded-lg gap-x-2 text-red-50 bg-red-500'
                                    }
                                >
                                    <IconCloudRain size={20} />
                                    <div>Rain has been detected but cover is not closed</div>
                                </div>
                            </div>
                        )}
                </>
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
                {(mainLogs === undefined || mainLogs.length === 0) && (
                    <div className="p-2">
                        <essentialComponents.Spinner />
                    </div>
                )}
                {mainLogs !== undefined &&
                    mainLogs
                        .slice(-15)
                        .map((l, i) => (
                            <essentialComponents.CoreLogLine key={`${i} ${l}`} text={l} />
                        ))}
            </div>
        </div>
    );
}
