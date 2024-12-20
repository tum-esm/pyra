import { useEffect, useState } from 'react';
import { essentialComponents } from '../components';
import { documentDir, downloadDir, join } from '@tauri-apps/api/path';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import * as shell from '@tauri-apps/plugin-shell';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../components/ui/select';
import { Separator } from '../components/ui/separator';

// TODO: add tab to render all logs

export default function LogTab() {
    const [logType, setLogType] = useState<
        | 'All'
        | 'Main'
        | 'OPUS'
        | 'CamTracker'
        | 'CAS'
        | 'System Health'
        | 'Upload'
        | 'TUM Enclosure'
        | 'Helios'
        | 'UI'
    >('Main');

    const [liveUpdateIsActice, setLiveUpdateIsActive] = useState(true);

    const [renderedAllLogs, setRenderedAllLogs] = useState<string[] | undefined>(undefined);
    const [renderedMainLogs, setRenderedMainLogs] = useState<string[] | undefined>(undefined);
    const [renderedOpusLogs, setRenderedOpusLogs] = useState<string[] | undefined>(undefined);
    const [renderedCamtrackerLogs, setRenderedCamtrackerLogs] = useState<string[] | undefined>(
        undefined
    );
    const [renderedCasLogs, setRenderedCasLogs] = useState<string[] | undefined>(undefined);
    const [renderedUploadLogs, setRenderedUploadLogs] = useState<string[] | undefined>(undefined);
    const [renderedTumEnclosureLogs, setRenderedTumEnclosureLogs] = useState<string[] | undefined>(
        undefined
    );
    const [renderedHeliosLogs, setRenderedHeliosLogs] = useState<string[] | undefined>(undefined);

    const { coreLogs, uiLogs } = useLogsStore();
    useEffect(() => {
        if (liveUpdateIsActice) {
            setRenderedAllLogs(coreLogs.all);
            setRenderedMainLogs(coreLogs.main);
            setRenderedOpusLogs(coreLogs.opus);
            setRenderedCamtrackerLogs(coreLogs.camtracker);
            setRenderedCasLogs(coreLogs.cas);
            setRenderedUploadLogs(coreLogs.upload);
            setRenderedTumEnclosureLogs(coreLogs.tum_enclosure);
            setRenderedHeliosLogs(coreLogs.helios);
        }
    }, [coreLogs, liveUpdateIsActice]);

    async function openLogsFolder() {
        let baseDir: string;
        let filePath: string;
        switch (import.meta.env.VITE_ENVIRONMENT) {
            // on moritz personal machine
            case 'development-moritz':
                baseDir = await documentDir();
                filePath = await join('work', 'esm', 'pyra', 'logs');
                break;

            // on the R19 laptop the Documents folder is a network directory
            // hence, we cannot use that one since some script do not run there
            case 'development-R19':
                baseDir = await downloadDir();
                filePath = await join('pyra', `pyra-${APP_VERSION}`, 'logs');
                break;

            // on all other systems (no development of PYRA)
            default:
                baseDir = await documentDir();
                filePath = await join('pyra', `pyra-${APP_VERSION}`, 'logs');
                break;
        }

        await shell.open(await join(baseDir, filePath));
    }

    const renderedLogs =
        logType === 'All'
            ? renderedAllLogs
            : logType === 'Main'
            ? renderedMainLogs
            : logType === 'OPUS'
            ? renderedOpusLogs
            : logType === 'CamTracker'
            ? renderedCamtrackerLogs
            : logType === 'CAS'
            ? renderedCasLogs
            : logType === 'System Health'
            ? coreLogs.system_health
            : logType === 'Upload'
            ? renderedUploadLogs
            : logType === 'TUM Enclosure'
            ? renderedTumEnclosureLogs
            : renderedHeliosLogs;

    return (
        <div className={'flex flex-col w-full h-[calc(100vh-3.5rem)] overflow-hidden '}>
            <div className="px-6 py-4 bg-white flex-row-center gap-x-2 ">
                <essentialComponents.LiveSwitch
                    isLive={liveUpdateIsActice}
                    toggle={setLiveUpdateIsActive}
                />
                {coreLogs === undefined && <essentialComponents.Spinner />}
                <Select onValueChange={(value) => setLogType(value as any)}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Main" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="All">All Logs</SelectItem>   
                        <SelectItem value="Main">Main</SelectItem>
                        <Separator className="my-1" />
                        <SelectItem value="OPUS">OPUS</SelectItem>
                        <SelectItem value="CamTracker">CamTracker</SelectItem>
                        <SelectItem value="CAS">CAS</SelectItem>
                        <SelectItem value="System Health">System Health</SelectItem>
                        <SelectItem value="Upload">Upload</SelectItem>
                        <Separator className="my-1" />
                        <SelectItem value="TUM Enclosure">TUM Enclosure</SelectItem>
                        <SelectItem value="Helios">Helios</SelectItem>
                        <Separator className="my-1" />
                        <SelectItem value="UI">UI</SelectItem>
                    </SelectContent>
                </Select>
                <div className="flex-grow" />
                <essentialComponents.Button onClick={openLogsFolder} variant="white">
                    open logs folder
                </essentialComponents.Button>
            </div>
            <div
                className={
                    'w-full !py-2 !mb-0 font-mono text-xs overflow-y-scroll ' +
                    'border-t border-gray-250 bg-whites flex-grow bg-slate-50'
                }
            >
                {logType !== 'UI' && renderedLogs !== undefined && (
                    <>
                        {renderedLogs.map((l, i) => (
                            <essentialComponents.CoreLogLine text={l} key={`${i} ${l}`} />
                        ))}
                        {renderedLogs.length == 0 && (
                            <div className="px-4 py-2">logs are empty</div>
                        )}
                    </>
                )}
                {logType === 'UI' && (
                    <>
                        {uiLogs.map((l, i) => (
                            <essentialComponents.UILogLine logLine={l} key={`${i} ${l.text}`} />
                        ))}
                        {uiLogs.length == 0 && <div className="px-4 py-2">logs are empty</div>}
                    </>
                )}
            </div>
        </div>
    );
}
