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
import { ChildProcess } from '@tauri-apps/api/shell';
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
                    'w-full text-sm flex flex-row items-center justify-center gap-x-2 px-4 py-2 h-14 flex-shrink-0 ' +
                    (pyraCorePid === undefined
                        ? 'bg-slate-300 text-slate-950'
                        : pyraCorePid === -1
                        ? 'bg-yellow-300 text-yellow-950 '
                        : 'bg-green-300 text-green-950')
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
                    <Button onClick={pyraCorePid === -1 ? startPyraCore : stopPyraCore}>
                        <IconPower size={18} />
                    </Button>
                )}
            </div>
            {coreState && centralConfig && (
                <div
                    className={
                        'flex flex-row items-center w-full p-3 text-sm text-green-900 border-y gap-x-2 px-4 h-14 ' +
                        (coreState.measurements_should_be_running === null
                            ? 'text-slate-950 bg-slate-300 border-slate-400'
                            : coreState.measurements_should_be_running
                            ? 'text-green-950 bg-green-300 border-green-400'
                            : 'text-yellow-950 bg-yellow-300 border-yellow-400')
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
