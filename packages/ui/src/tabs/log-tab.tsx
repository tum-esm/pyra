import { useEffect, useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { watch } from 'tauri-plugin-fs-watch-api';
import { backend, reduxUtils } from '../utils';
import { essentialComponents } from '../components';

export default function LogTab(props: { visible: boolean }) {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);
    const [loading, setLoading] = useState(false);
    const [loadingIsPending, setLoadingIsPending] = useState(true);

    const logsState = reduxUtils.useTypedSelector((s) => s.logs);
    const dispatch = reduxUtils.useTypedDispatch();

    async function updateLogs() {
        setLoading(true);
        setLoadingIsPending(false);
        try {
            const newLogLines = (await backend.readDebugLogs()).stdout.split('\n');
            dispatch(reduxUtils.logsActions.set(newLogLines));
        } catch {
            // TODO: Add message to queue
        } finally {
            setLoading(false);
        }
    }

    async function archiveLogs() {
        if (await dialog.confirm('Do you want to archive all current logs?', 'PyRa 4 UI')) {
            setArchiving(true);
            await backend.archiveLogs();
            setArchiving(false);
            await updateLogs();
        }
    }

    async function openLogsFolder() {
        await shell.open(`${import.meta.env.VITE_PROJECT_DIR}/logs`);
    }

    useEffect(() => {
        initializeFileWatcher();
    }, []);

    useEffect(() => {
        if (loadingIsPending && !loading) {
            updateLogs();
        }
    }, [loadingIsPending, loading, updateLogs]);

    // TODO: Move filewatcher to top level component
    async function initializeFileWatcher() {
        let logFilePath = import.meta.env.VITE_PROJECT_DIR + '\\logs\\info.log';
        if (window.navigator.platform.includes('Mac')) {
            logFilePath = logFilePath.replace(/\\/g, '/');
        }
        await watch(logFilePath, { recursive: false }, (o) =>
            setLoadingIsPending(o.type === 'Write')
        );
    }

    return (
        <div className={'flex-col w-full h-full pt-4 ' + (props.visible ? 'flex ' : 'hidden ')}>
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <essentialComponents.Toggle
                    value={logLevel}
                    setValue={(s: any) => setLogLevel(s)}
                    values={['info', 'debug']}
                />
                {loading && <essentialComponents.Spinner />}
                <div className="flex-grow" />
                <essentialComponents.Button onClick={openLogsFolder} variant="white">
                    open logs folder
                </essentialComponents.Button>
                <essentialComponents.Button
                    onClick={archiveLogs}
                    variant="red"
                    spinner={archiving}
                    disabled={loading}
                >
                    archive logs
                </essentialComponents.Button>
            </div>
            <pre
                className={
                    'w-full !px-6 !py-2 !mb-0 overflow-y-scroll ' +
                    'border-t border-slate-300 bg-white h-full'
                }
            >
                <code className="w-full h-full !text-xs language-log">
                    {(logLevel === 'info' ? logsState.infoLines : logsState.debugLines).join('\n')}
                    {logsState.areEmpty && <strong>logs are empty</strong>}
                </code>
            </pre>
        </div>
    );
}
