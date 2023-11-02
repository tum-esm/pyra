import toast from 'react-hot-toast';
import { fetchUtils } from '../../utils';
import { useCoreProcessStore } from '../../utils/zustand-utils/core-process-zustand';
import { Button } from '../ui/button';
import { IconPower } from '@tabler/icons-react';
import { useEffect } from 'react';
import { ChildProcess } from '@tauri-apps/api/shell';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = useCoreProcessStore();
    const { addUiLogLine } = useLogsStore();

    function exitFromFailedProcess(p: ChildProcess, label: string): string {
        addUiLogLine(`Error while ${label}.`, `stdout = ${p.stdout}, stderr = ${p.stderr}`);
        return `Error while ${label}, full error in UI logs`;
    }

    function checkPyraCoreState() {
        toast.promise(fetchUtils.backend.checkPyraCoreState(), {
            loading: 'checking Pyra Core state',
            success: (p: ChildProcess) => {
                if (p.stdout.includes('not running')) {
                    setPyraCorePid(-1);
                    return 'Pyra Core is not running';
                } else {
                    setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                    return 'Pyra Core is running';
                }
            },
            error: (p: ChildProcess) => exitFromFailedProcess(p, 'checking Pyra Core state'),
        });
    }

    useEffect(checkPyraCoreState, []);

    async function startPyraCore(): Promise<void> {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.startPyraCore(), {
            loading: 'starting Pyra Core',
            success: (p: ChildProcess) => {
                setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                return 'Pyra Core has been started';
            },
            error: (p: ChildProcess) => exitFromFailedProcess(p, 'starting Pyra Core'),
        });
    }

    async function stopPyraCore() {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.stopPyraCore(), {
            loading: 'stopping Pyra Core',
            success: (p: ChildProcess) => {
                setPyraCorePid(-1);
                return 'Pyra Core has been stopped';
            },
            error: (p: ChildProcess) => {
                checkPyraCoreState();
                return exitFromFailedProcess(p, 'stopping Pyra Core');
            },
        });
    }

    return (
        <div
            className={
                'w-full text-sm flex flex-row items-center justify-center gap-x-2 px-4 py-2 h-14 flex-shrink-0 ' +
                (pyraCorePid === undefined
                    ? 'bg-slate-200 text-slate-950'
                    : pyraCorePid === -1
                    ? 'bg-yellow-300 text-yellow-950 '
                    : 'bg-green-300 text-green-950')
            }
        >
            <div>
                {pyraCorePid === undefined && '...'}
                {pyraCorePid === -1 && (
                    <span>
                        Pyra Core is <strong className="font-semibold">not running</strong>
                    </span>
                )}
                {pyraCorePid !== undefined && pyraCorePid !== -1 && (
                    <span>
                        Pyra Core is <strong className="font-semibold">running</strong> with process
                        ID {pyraCorePid}
                    </span>
                )}
            </div>
            <div className="flex-grow" />
            {pyraCorePid !== undefined && (
                <Button onClick={pyraCorePid === -1 ? startPyraCore : stopPyraCore}>
                    <IconPower size={18} />
                </Button>
            )}
        </div>
    );
}
