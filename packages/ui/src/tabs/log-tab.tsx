import { useMemo, useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { fetchUtils, functionalUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import toast from 'react-hot-toast';
import { documentDir, downloadDir, join } from '@tauri-apps/api/path';

export default function LogTab() {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);

    const dispatch = reduxUtils.useTypedDispatch();

    const fetchUpdates = reduxUtils.useTypedSelector((s) => s.logs.fetchUpdates);
    const setFetchUpdates = (f: boolean) => dispatch(reduxUtils.logsActions.setFetchUpdates(f));

    const renderedLogScope = reduxUtils.useTypedSelector((s) => s.logs.renderedLogScope);
    const setRenderedLogScope = (f: '3 iterations' | '5 minutes') =>
        dispatch(reduxUtils.logsActions.setRenderedLogScope(f));

    const debugLogLines = reduxUtils.useTypedSelector((s) => s.logs.debugLines);
    const infoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);

    const renderedLogLines: string[] | undefined = useMemo(() => {
        if (debugLogLines === undefined || infoLogLines === undefined) {
            return undefined;
        }
        let leveledLines = logLevel === 'info' ? infoLogLines : debugLogLines;
        if (renderedLogScope === '3 iterations') {
            leveledLines = functionalUtils.reduceLogLines(leveledLines, '3 iterations');
        }
        return leveledLines;
    }, [debugLogLines, infoLogLines, logLevel, renderedLogScope]);

    async function openLogsFolder() {
        let baseDir: string;
        let filePath: string;
        switch (import.meta.env.VITE_ENVIRONMENT) {
            // on moritz personal machine
            case 'development-moritz':
                baseDir = await documentDir();
                filePath = await join('research', 'pyra-4', 'logs');
                break;

            // on the R19 laptop the Documents folder is a network directory
            // hence, we cannot use that one since some script do not run there
            case 'development-R19':
                baseDir = await downloadDir();
                filePath = await join('pyra-4', 'logs');
                break;

            // on all other systems (no development of PYRA)
            default:
                baseDir = await documentDir();
                filePath = await join('pyra', `pyra-${APP_VERSION}`, 'logs');
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

    return (
        <div className={'flex flex-col w-full h-[calc(100vh-3.5rem)] pt-4 overflow-hidden '}>
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <essentialComponents.LiveSwitch isLive={fetchUpdates} toggle={setFetchUpdates} />
                <essentialComponents.Toggle
                    value={logLevel}
                    setValue={(s: any) => setLogLevel(s)}
                    values={['info', 'debug']}
                />
                <essentialComponents.Toggle
                    value={renderedLogScope}
                    setValue={setRenderedLogScope}
                    values={['3 iterations', '5 minutes']}
                />
                {renderedLogLines === undefined && <essentialComponents.Spinner />}
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
                    'w-full !py-2 !mb-0 font-mono text-xs overflow-y-scroll ' +
                    'border-t border-gray-250 bg-whites flex-grow bg-white'
                }
            >
                {renderedLogLines !== undefined && (
                    <>
                        {renderedLogLines.map((l, i) => (
                            <essentialComponents.LogLine text={l} key={`${i} ${l}`} />
                        ))}
                        {renderedLogLines.length == 0 && <strong>logs are empty</strong>}
                    </>
                )}
            </div>
        </div>
    );
}
