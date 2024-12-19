import { fetchUtils } from '../../utils';
import { useCoreProcessStore } from '../../utils/zustand-utils/core-process-zustand';
import { Button } from '../ui/button';
import {
    IconCpu,
    IconCpuOff,
    IconMicroscope,
    IconMicroscopeOff,
    IconPower,
} from '@tabler/icons-react';
import { useEffect } from 'react';
import { ChildProcess } from '@tauri-apps/plugin-shell';
import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = useCoreProcessStore();
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { coreState } = useCoreStateStore();
    const { centralConfig } = useConfigStore();

    function checkPyraCoreState() {
        runPromisingCommand({
            command: fetchUtils.backend.checkPyraCoreState,
            label: 'checking Pyra Core state',
            successLabel: 'successfully checked Pyra Core state',
            onSuccess: (p: ChildProcess) => {
                if (p.stdout.includes('not running')) {
                    setPyraCorePid(-1);
                } else {
                    setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                }
            },
            onError: (p: ChildProcess) => checkPyraCoreState(),
        });
    }

    function startPyraCore() {
        setPyraCorePid(undefined);
        runPromisingCommand({
            command: fetchUtils.backend.startPyraCore,
            label: 'starting Pyra Core',
            successLabel: 'successfully started Pyra Core',
            onSuccess: (p: ChildProcess) => {
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
            onError: (p: ChildProcess) => checkPyraCoreState(),
        });
    }

    useEffect(checkPyraCoreState, []);

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
                        System is{' '}
                        <strong className="font-semibold">
                            {!coreState.measurements_should_be_running && 'not'} measuring
                        </strong>
                        {coreState.measurements_should_be_running === null && ' during startup'}
                    </div>
                </div>
            )}
        </>
    );
}
