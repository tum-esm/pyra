import toast from 'react-hot-toast';
import { fetchUtils } from '../../utils';
import { usePyraCoreStore } from '../../utils/zustand-utils/core-state-zustand';
import { Button } from '../ui/button';
import { IconPower } from '@tabler/icons-react';
import { useEffect } from 'react';
import { ChildProcess } from '@tauri-apps/api/shell';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = usePyraCoreStore();

    useEffect(() => {
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
            error: (p: ChildProcess) => {
                return `Could not determine, whether Pyra Core is Running: ${p}`;
            },
        });
    }, []);

    async function startPyraCore(): Promise<void> {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.startPyraCore(), {
            loading: 'starting Pyra Core',
            success: (p: ChildProcess) => {
                setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                return 'Pyra Core has been started';
            },
            error: (p: ChildProcess) => `Error while starting Pyra Core: ${p}`,
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
            error: (p: ChildProcess) => `Error while stopping Pyra Core: ${p}`,
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
