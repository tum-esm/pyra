import toast from 'react-hot-toast';
import { fetchUtils } from '../../utils';
import { usePyraCoreStore } from '../../utils/zustand-utils/pyra-core-zustand';
import { Button } from '../ui/button';

export default function PyraCoreStatus() {
    const { pyraCorePid, setPyraCorePid } = usePyraCoreStore();

    async function stopPyraCore() {
        setPyraCorePid(undefined);
        toast.promise(fetchUtils.backend.stopPyraCore(), {
            loading: 'stopping Pyra Core',
            success: () => {
                setPyraCorePid(-1);
                return 'Pyra Core has been stopped';
            },
            error: 'Error while stopping Pyra Core',
        });
    }

    const pid = pyraCorePid === -1 ? undefined : pyraCorePid;

    return (
        <div
            className={
                'w-full text-sm flex flex-row items-center justify-center gap-x-2 px-4 py-2 bg-green-300 text-green-900'
            }
        >
            <div>
                <span className="ml-2.5 mr-1">Pyra Core is</span>
                {pid === undefined && (
                    <span className="font-semibold text-green-950">not running</span>
                )}
                {pid !== undefined && (
                    <>
                        running with{' '}
                        <span className="font-semibold text-green-950">process ID {pid}</span>
                    </>
                )}
            </div>
            <div className="flex-grow" />
            <Button onClick={stopPyraCore} className="bg-green-900 hover:bg-green-700">
                stop Pyra Core
            </Button>
        </div>
    );
}
