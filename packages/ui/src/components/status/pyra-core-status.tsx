import { useEffect } from 'react';
import backend from '../../utils/backend';
import Button from '../essential/button';
import Ping from '../essential/ping';

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
        <div className={'w-full text-sm flex-row-left gap-x-2 px-6'}>
            <div className="flex-grow text-sm h-7 flex-row-left">
                <Ping
                    state={pyraCorePID === undefined ? undefined : pyraCorePID !== -1}
                />
                <span className="ml-2.5 mr-1">pyra-core is</span>
                {pyraCorePID === undefined && '...'}
                {pyraCorePID !== undefined && pyraCorePID === -1 && 'not running'}
                {pyraCorePID !== undefined &&
                    pyraCorePID !== -1 &&
                    `running with process ID ${pyraCorePID}`}
            </div>
            <Button
                onClick={pyraCorePID === -1 ? startPyraCore : stopPyraCore}
                className="w-[21rem]"
                variant={pyraCorePID === -1 ? 'green' : 'red'}
            >
                {pyraCorePID === -1 ? 'start' : 'stop'}
            </Button>
        </div>
    );
}