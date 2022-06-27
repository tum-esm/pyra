import { useEffect } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { essentialComponents } from '..';

export default function PyraCoreStatus() {
    const coreProcessPID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
    const dispatch = reduxUtils.useTypedDispatch();
    const setCoreProcessPID = (pid: number | undefined) =>
        dispatch(reduxUtils.coreProcessActions.set({ pid }));

    async function updatePyraCoreIsRunning() {
        const p = await fetchUtils.backend.checkPyraCoreState();
        if (p.stdout.includes('pyra-core is running with PID')) {
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setCoreProcessPID(pid);
        } else {
            setCoreProcessPID(-1);
        }
    }
    useEffect(() => {
        updatePyraCoreIsRunning();
    }, []);

    async function startPyraCore() {
        setCoreProcessPID(undefined);
        try {
            const p = await fetchUtils.backend.startPyraCore();
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setCoreProcessPID(pid);
        } catch {
            // TODO: add message to queue
            setCoreProcessPID(undefined);
        }
    }

    async function stopPyraCore() {
        setCoreProcessPID(undefined);
        await fetchUtils.backend.stopPyraCore();
        setCoreProcessPID(-1);
    }

    return (
        <div className={'w-full text-sm flex-row-left gap-x-2 px-6'}>
            <div className="flex-grow text-sm h-7 flex-row-left">
                <essentialComponents.Ping
                    state={coreProcessPID === undefined ? undefined : coreProcessPID !== -1}
                />
                <span className="ml-2.5 mr-1">pyra-core is</span>
                {coreProcessPID === undefined && <essentialComponents.Spinner />}
                {coreProcessPID !== undefined && (
                    <>
                        {coreProcessPID === -1 && 'not running'}
                        {coreProcessPID !== -1 && `running with process ID ${coreProcessPID}`}
                    </>
                )}
            </div>
            <essentialComponents.Button
                onClick={coreProcessPID === -1 ? startPyraCore : stopPyraCore}
                className="w-[21rem]"
                variant={
                    coreProcessPID === undefined ? 'gray' : coreProcessPID === -1 ? 'green' : 'red'
                }
                spinner={coreProcessPID === undefined}
            >
                {coreProcessPID === -1 ? 'start' : 'stop'}
            </essentialComponents.Button>
        </div>
    );
}
