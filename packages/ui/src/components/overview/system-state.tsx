import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { mean } from 'lodash';
import { renderString } from '../../utils/functions';

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

    if (!coreState) {
        return <></>;
    }

    return (
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
            <StatePanel title="Current Sun Elevation">
                {renderString(coreState?.position.sun_elevation, {
                    appendix: ' °',
                })}
            </StatePanel>
        </div>
    );
}
