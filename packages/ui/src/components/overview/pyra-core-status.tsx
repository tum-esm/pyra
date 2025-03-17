import { fetchUtils } from '../../utils';
import { useCoreProcessStore } from '../../utils/zustand-utils/core-process-zustand';
import {
    IconCpu,
    IconCpuOff,
    IconMicroscope,
    IconMicroscopeOff,
    IconPower,
} from '@tabler/icons-react';
import { ChildProcess } from '@tauri-apps/plugin-shell';
import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = useCoreProcessStore();
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { coreState } = useCoreStateStore();
    const { centralConfig } = useConfigStore();
    const { coreLogs } = useLogsStore();

    function startPyraCore() {
        setPyraCorePid(undefined);
        runPromisingCommand({
            command: fetchUtils.backend.startPyraCore,
            label: 'starting Pyra Core',
            successLabel: 'successfully started Pyra Core',
            onSuccess: (p: ChildProcess<string>) => {
                setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
            },
        });
    }

    function stopPyraCore() {
        setPyraCorePid(undefined);
        runPromisingCommand({
            command: fetchUtils.backend.stopPyraCore,
            label: 'stopping Pyra Core',
            successLabel: 'successfully stopped Pyra Core',
            onSuccess: () => setPyraCorePid(-1),
        });
    }

    let measurementStatusRemarks: string | undefined = undefined;
    if (coreState && centralConfig) {
        const sun_elevation = coreState.position.sun_elevation;
        const min_sun_elevation = centralConfig.general.min_sun_elevation;
        if (sun_elevation !== null) {
            if (sun_elevation < min_sun_elevation) {
                measurementStatusRemarks = `Sun elevation (${sun_elevation.toFixed(
                    2
                )}°) is below minimum (${min_sun_elevation}°)`;
            }
        }
        if (measurementStatusRemarks === undefined && coreLogs.cas) {
            let rainBlock = false;
            coreLogs.cas.forEach((log) => {
                if (
                    log.includes(
                        'Not trying to measure when rain was detected within the last 3 minutes.'
                    )
                ) {
                    rainBlock = true;
                }
            });
            if (rainBlock) {
                measurementStatusRemarks = 'Rain was detected within the last 3 minutes';
            }
        }
    }

    return (
        <>
            <div
                className={
                    'w-full text-sm flex flex-row items-center justify-center gap-x-2 pl-4 py-2 h-10 flex-shrink-0 rounded-lg ' +
                    (pyraCorePid === undefined
                        ? 'bg-slate-100 text-slate-400 border border-slate-200 '
                        : pyraCorePid === -1
                        ? 'bg-slate-100 text-slate-950 border border-slate-200 '
                        : 'bg-green-300 text-green-950 border border-green-400')
                }
            >
                {pyraCorePid === undefined && '...'}
                {pyraCorePid === -1 && (
                    <>
                        <IconCpuOff size={18} />
                        <span>
                            Pyra Core is <strong className="font-semibold">not running</strong>
                        </span>
                    </>
                )}
                {pyraCorePid !== undefined && pyraCorePid !== -1 && (
                    <>
                        <IconCpu size={18} />
                        <span>
                            Pyra Core is <strong className="font-semibold">running</strong> with
                            process ID {pyraCorePid}
                        </span>
                    </>
                )}
                <div className="flex-grow" />
                {pyraCorePid !== undefined && (
                    <button
                        onClick={pyraCorePid === -1 ? startPyraCore : stopPyraCore}
                        className={
                            'flex items-center justify-center w-12 h-10 rounded-r-lg ' +
                            (pyraCorePid === -1
                                ? 'bg-slate-200 hover:bg-slate-300 text-slate-700 hover:text-slate-950'
                                : 'bg-green-400 hover:bg-green-500')
                        }
                    >
                        <IconPower size={18} />
                    </button>
                )}
            </div>
            {coreState && centralConfig && pyraCorePid !== undefined && pyraCorePid != -1 && (
                <div
                    className={
                        'flex flex-row items-center w-full rounded-lg p-3 text-sm gap-x-2 px-4 h-10 ' +
                        (coreState.measurements_should_be_running === null
                            ? 'text-slate-400 bg-slate-100 border border-slate-200 '
                            : coreState.measurements_should_be_running
                            ? 'bg-green-300 text-green-950 border border-green-400'
                            : 'text-slate-950 bg-slate-100 border border-slate-200 ')
                    }
                >
                    {coreState.measurements_should_be_running ? (
                        <IconMicroscope size={18} />
                    ) : (
                        <IconMicroscopeOff size={18} />
                    )}
                    <div>
                        {coreState.measurements_should_be_running == true && 'System is measuring'}
                        {coreState.measurements_should_be_running === false &&
                            'System is not measuring'}
                        {coreState.measurements_should_be_running == null &&
                            'System is not measuring during startup'}

                        {coreState.measurements_should_be_running === false &&
                            centralConfig.measurement_decision.mode == 'manual' &&
                            centralConfig.measurement_decision.manual_decision_result &&
                            measurementStatusRemarks !== undefined &&
                            ` (${measurementStatusRemarks})`}
                    </div>
                </div>
            )}
        </>
    );
}
