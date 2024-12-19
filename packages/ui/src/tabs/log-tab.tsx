import { useEffect, useState } from 'react';
import {  } from '@tauri-apps/api';
import { essentialComponents } from '../components';
import { documentDir, downloadDir, join } from '@tauri-apps/api/path';
import Toggle from '../components/essential/toggle';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import * as shell from "@tauri-apps/plugin-shell"

export default function LogTab() {
    const [logType, setLogType] = useState<'main' | 'upload' | 'helios' | 'ui'>('main');

    const [liveUpdateIsActice, setLiveUpdateIsActive] = useState(true);
    const [renderedMainLogs, setRenderedMainLogs] = useState<string[] | undefined>(undefined);
    const [renderedUploadLogs, setRenderedUploadLogs] = useState<string[] | undefined>(undefined);
    const [renderedHeliosLogs, setRenderedHeliosLogs] = useState<string[] | undefined>(undefined);

    const { mainLogs, uploadLogs, heliosLogs, uiLogs } = useLogsStore();
    useEffect(() => {
        if (liveUpdateIsActice) {
            setRenderedMainLogs(mainLogs);
            setRenderedUploadLogs(uploadLogs);
            setRenderedHeliosLogs(heliosLogs);
        }
    }, [mainLogs, uploadLogs, heliosLogs, liveUpdateIsActice]);

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
        logType === 'main'
            ? renderedMainLogs
            : logType === 'upload'
            ? renderedUploadLogs
            : renderedHeliosLogs;

    return (
        <div className={'flex flex-col w-full h-[calc(100vh-3.5rem)] overflow-hidden '}>
            <div className="px-6 py-4 bg-white flex-row-center gap-x-2 ">
                <essentialComponents.LiveSwitch
                    isLive={liveUpdateIsActice}
                    toggle={setLiveUpdateIsActive}
                />
                {mainLogs === undefined && <essentialComponents.Spinner />}
                <Toggle
                    value={logType}
                    setValue={(lt: any) => setLogType(lt)}
                    values={['main', 'upload', 'helios', 'ui']}
                />
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
                {logType !== 'ui' && renderedLogs !== undefined && (
                    <>
                        {renderedLogs.map((l, i) => (
                            <essentialComponents.CoreLogLine text={l} key={`${i} ${l}`} />
                        ))}
                        {renderedLogs.length == 0 && (
                            <div className="px-4 py-2">logs are empty</div>
                        )}
                    </>
                )}
                {logType === 'ui' && (
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
