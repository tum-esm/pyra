import { useEffect } from 'react';
import backend from '../../utils/backend';

export default function PyraCoreStatus(props: {
    pyraCorePID: number | undefined;
    setPyraCorePID(p: number | undefined): void;
}) {
    const { pyraCorePID, setPyraCorePID } = props;

    async function updatePyraCoreIsRunning() {
        const p = await backend.checkPyraCoreState();
        if (p.stdout.includes('pyra-core is running with PID')) {
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setPyraCorePID(pid);
        } else {
            setPyraCorePID(-1);
        }
    }
    useEffect(() => {
        updatePyraCoreIsRunning();
    }, []);

    async function startPyraCore() {
        setPyraCorePID(undefined);
        const p = await backend.startPyraCore();
        const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
        // TODO: add message to queue
        setPyraCorePID(pid);
    }

    async function stopPyraCore() {
        setPyraCorePID(undefined);
        await backend.stopPyraCore();
        setPyraCorePID(-1);
    }

    return (
        <div
            className={
                'w-full text-sm bg-white border border-gray-300 ' +
                'rounded-md shadow-sm flex-row-left'
            }
        >
            <div className="px-3 font-normal flex-row-left">
                pyra-core is{' '}
                {pyraCorePID === undefined && (
                    <span className="ml-1 mr-4 font-semibold">...</span>
                )}
                {pyraCorePID !== undefined && (
                    <span className="ml-1 mr-4">
                        {pyraCorePID === -1 && (
                            <span className="font-semibold text-red-600">
                                not running
                            </span>
                        )}
                        {pyraCorePID !== -1 && (
                            <>
                                <span className="font-semibold text-green-600">
                                    running
                                </span>{' '}
                                with process ID {pyraCorePID}
                            </>
                        )}
                    </span>
                )}
            </div>
            <div className="flex-grow" />
            <button
                onClick={pyraCorePID === -1 ? startPyraCore : stopPyraCore}
                className={
                    'px-3 py-1.5 rounded-r-md border-l border-gray-300 font-medium w-16 ' +
                    (pyraCorePID === -1
                        ? 'bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-900 '
                        : 'bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-900 ')
                }
            >
                {pyraCorePID === -1 ? 'start' : 'stop'}
            </button>
        </div>
    );
}
