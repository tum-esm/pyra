import { useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import toast from 'react-hot-toast';
import { documentDir, downloadDir, join } from '@tauri-apps/api/path';

export default function LogTab() {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);

    const debugLogLines = reduxUtils.useTypedSelector((s) => s.logs.debugLines);
    const infoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
    const fetchUpdates = reduxUtils.useTypedSelector((s) => s.logs.fetchUpdates);
    const setFetchUpdates = (f: boolean) => dispatch(reduxUtils.logsActions.setFetchUpdates(f));

    const dispatch = reduxUtils.useTypedDispatch();

    async function openLogsFolder() {
        let baseDir = await documentDir();
        let filePath = await join('pyra-4', 'logs', 'debug.log');
        switch (import.meta.env.VITE_ENVIRONMENT) {
            // on my personal machine
            case 'development-moritz':
                filePath = await join('research', filePath);
                break;

            // on the R19 laptop the Documents folder is a network directory
            // hence, we cannot use that one since some script do not run there
            case 'development-R19':
                baseDir = await downloadDir();
                break;
        }

        await shell.open(await join(baseDir, filePath));
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

    // TODO: Make min-window-size larger
    // TODO: Toggle between log times: "2 iterations" | "3 minutes" | "15 minutes" | "60 minutes"

    return (
        <div className={'flex-col w-full h-full pt-4 '}>
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <essentialComponents.LiveSwitch isLive={fetchUpdates} toggle={setFetchUpdates} />
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
            <div
                className={
                    'w-full !py-2 !mb-0 font-mono text-xs ' +
                    'border-t border-gray-250 bg-white flex-grow'
                }
            >
                {!logsAreLoading && (
                    <>
                        {(logLevel === 'info' ? infoLogLines : debugLogLines).map((l, i) => (
                            <essentialComponents.LogLine text={l} key={`${i} ${l}`} />
                        ))}
                        {debugLogLines.length == 0 && <strong>logs are empty</strong>}
                    </>
                )}
            </div>
        </div>
    );
}
