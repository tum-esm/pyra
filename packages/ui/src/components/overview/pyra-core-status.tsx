import toast from 'react-hot-toast';
import { fetchUtils } from '../../utils';
import { usePyraCoreStore } from '../../utils/zustand-utils/core-state-zustand';
import { Button } from '../ui/button';
import { IconPower } from '@tabler/icons-react';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = usePyraCoreStore();

    async function startPyraCore(): Promise<void> {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.stopPyraCore(), {
            loading: 'starting Pyra Core',
            success: (p) => {
                setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                return 'Pyra Core has been started';
            },
            error: (e) => `Error while starting Pyra Core: ${e}`,
        });
    }

    async function stopPyraCore() {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.stopPyraCore(), {
            loading: 'stopping Pyra Core',
            success: () => {
                setPyraCorePid(-1);
                return 'Pyra Core has been stopped';
            },
            error: (e) => `Error while stopping Pyra Core: ${e}`,
        });
    }

    return (
        <div
            className={
                'w-full text-sm flex flex-row items-center justify-center gap-x-2 px-4 py-2 ' +
                (pyraCorePid === undefined
                    ? 'bg-slate-300 text-slate-950'
                    : pyraCorePid === -1
                    ? 'bg-red-300 text-red-950'
                    : 'bg-green-300 text-green-950')
            }
        >
            <div>
                {pyraCorePid === undefined && 'loading'}
                {pyraCorePid === -1 && (
                    <span>
                        Pyra Core is
                        <strong className="font-semibold">not running</strong>
                    </span>
                )}
                {pyraCorePid !== undefined && pyraCorePid !== -1 && (
                    <span>
                        Pyra Core is
                        <strong className="font-semibold">running</strong> with process ID{' '}
                        {pyraCorePid}
                    </span>
                )}
            </div>
            <div className="flex-grow" />
            {pyraCorePid !== undefined && (
                <Button
                    onClick={pyraCorePid === -1 ? startPyraCore : stopPyraCore}
                    className={
                        pyraCorePid === -1
                            ? 'bg-red-900 hover:bg-red-700'
                            : 'bg-green-900 hover:bg-green-700'
                    }
                >
                    <IconPower size={18} />
                </Button>
            )}
        </div>
    );
}
