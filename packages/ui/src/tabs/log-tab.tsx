import { useState } from 'react';
import { dialog, shell } from '@tauri-apps/api';
import { fetchUtils, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import toast from 'react-hot-toast';
import { drop } from 'lodash';
import { documentDir, downloadDir, join } from '@tauri-apps/api/path';

function RenderedLogLine(props: { l: string }) {
    if (props.l == 'More log lines inside logs folder ...') {
        return <pre className="font-light text-gray-500">{props.l}</pre>;
    }
    if (props.l.includes('EXCEPTION')) {
        return <pre className="font-bold text-red-700">{props.l}</pre>;
    }
    // FIXME: Debug traceback rendering
    // TODO: Highlight traceback lines with

    let l = props.l.replace(/\n/g, '');

    try {
        const timeSection = l.slice(11, 26);
        const sections = l.slice(29, undefined).split(' - ');
        const sourceSection = sections[0];
        const typeSection = sections[1];
        const messageSection = drop(sections, 2).join(' - ');

        let textStyle = 'text-gray-500 font-light';
        switch (typeSection) {
            case 'INFO':
                textStyle = 'text-gray-900 font-semibold';
                break;
            case 'WARNING':
            case 'CRITICAL':
            case 'ERROR':
                textStyle = 'text-red-700 font-bold';
                break;
        }

        // TODO: Highlight "starting mainloop" with a background color

        return (
            <>
                {messageSection.includes('Starting Iteration') && (
                    <div className="flex-shrink-0 h-px my-1 bg-gray-250 w-[calc(100%+2rem)] -ml-4 first:hidden" />
                )}
                <div className={`flex-row-left gap-x-3 ${textStyle} whitespace-nowrap mr-3`}>
                    <div>{timeSection}</div>
                    <div className="flex-shrink-0 w-44">{sourceSection}</div>
                    <div className="flex-shrink-0 w-12">{typeSection}</div>
                    <div>{messageSection}</div>
                </div>
            </>
        );
    } catch {
        return <></>;
    }
}

export default function LogTab() {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [archiving, setArchiving] = useState(false);

    const debugLogLines = reduxUtils.useTypedSelector((s) => s.logs.debugLines);
    const infoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
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
    // TODO: Add "live" | "paused" toggle
    // TODO: Toggle between log times: "2 iterations" | "3 minutes" | "15 minutes" | "60 minutes"

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
                    'w-full !px-4 !py-2 !mb-0 overflow-x-auto ' +
                    'border-t border-gray-300 bg-white flex-grow'
                }
            >
                {!logsAreLoading && (
                    <code className="w-full h-full !text-xs language-log">
                        {(logLevel === 'info' ? infoLogLines : debugLogLines).map((l) => (
                            <RenderedLogLine l={l} key={l} />
                        ))}
                        {debugLogLines.length == 0 && <strong>logs are empty</strong>}
                    </code>
                )}
            </pre>
        </div>
    );
}
