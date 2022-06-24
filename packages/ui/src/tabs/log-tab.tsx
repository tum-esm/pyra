import { useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { backend, reduxUtils } from '../utils';
import { essentialComponents } from '../components';

export default function LogTab() {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);

    const logsState = reduxUtils.useTypedSelector((s) => s.logs);
    const dispatch = reduxUtils.useTypedDispatch();

    async function openLogsFolder() {
        await shell.open(`${import.meta.env.VITE_PROJECT_DIR}/logs`);
    }

    async function archiveLogs() {
        if (await dialog.confirm('Do you want to archive all current logs?', 'PyRa 4 UI')) {
            setArchiving(true);
            await backend.archiveLogs();
            dispatch(reduxUtils.logsActions.set([]));
            setArchiving(false);
        }
    }

    return (
        <div className={'flex-col w-full h-full pt-4 '}>
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <essentialComponents.Toggle
                    value={logLevel}
                    setValue={(s: any) => setLogLevel(s)}
                    values={['info', 'debug']}
                />
                {logsState.loading && <essentialComponents.Spinner />}
                <div className="flex-grow" />
                <essentialComponents.Button onClick={openLogsFolder} variant="white">
                    open logs folder
                </essentialComponents.Button>
                <essentialComponents.Button
                    onClick={archiveLogs}
                    variant="red"
                    spinner={archiving}
                    disabled={logsState.loading}
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
                    {logsState.empty && <strong>logs are empty</strong>}
                </code>
            </pre>
        </div>
    );
}
