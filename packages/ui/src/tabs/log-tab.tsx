import { useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import toast from 'react-hot-toast';

export default function LogTab() {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);

    const debugLogLines = reduxUtils.useTypedSelector((s) => s.logs.debugLines);
    const infoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
    const dispatch = reduxUtils.useTypedDispatch();

    async function openLogsFolder() {
        await shell.open(`${import.meta.env.VITE_PROJECT_DIR}/logs`);
    }

    async function archiveLogs() {
        if (await dialog.confirm('Do you want to archive all current logs?', 'PyRa 4 UI')) {
            setArchiving(true);
            const result = await fetchUtils.backend.archiveLogs();
            if (result.stdout.replace(/[\n\s]*/g, '') === 'done!') {
                dispatch(reduxUtils.logsActions.set([]));
            } else {
                console.error(
                    `Could not archive log files. processResult = ${JSON.stringify(result)}`
                );
                toast.error(`Could not archive log files, please look in the console for details`);
            }
            setArchiving(false);
        }
    }

    const logsAreLoading = debugLogLines === undefined || infoLogLines === undefined;

    return (
        <div className={'flex-col w-full h-full pt-4 '}>
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <essentialComponents.Toggle
                    value={logLevel}
                    setValue={(s: any) => setLogLevel(s)}
                    values={['info', 'debug']}
                />
                {logsAreLoading && <essentialComponents.Spinner />}
                <div className="flex-grow" />
                <essentialComponents.Button onClick={openLogsFolder} variant="white">
                    open logs folder
                </essentialComponents.Button>
                <essentialComponents.Button onClick={archiveLogs} variant="red" spinner={archiving}>
                    archive logs
                </essentialComponents.Button>
            </div>
            <pre
                className={
                    'w-full !px-6 !py-2 !mb-0 overflow-y-scroll ' +
                    'border-t border-gray-300 bg-white flex-grow'
                }
            >
                {!logsAreLoading && (
                    <code className="w-full h-full !text-xs language-log">
                        {(logLevel === 'info' ? infoLogLines : debugLogLines).join('\n')}
                        {debugLogLines.length == 0 && <strong>logs are empty</strong>}
                    </code>
                )}
            </pre>
        </div>
    );
}
