import { useEffect, useState } from 'react';
import Toggle from '../components/essential/toggle';
import ICONS from '../assets/icons';
import Button from '../components/essential/button';
import backend from '../utils/backend';
import { dialog } from '@tauri-apps/api';

export default function LogTab(props: { visible: boolean }) {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [infoLogs, setInfoLogs] = useState<string>('');
    const [debugLogs, setDebugLogs] = useState<string>('');

    async function updateLogs() {
        setInfoLogs((await backend.readInfoLogs()).reverse().join('\n'));
        setDebugLogs((await backend.readDebugLogs()).reverse().join('\n'));
    }

    // TODO: show dialog
    async function archiveLogs() {
        if (
            await dialog.confirm(
                'Do you want to archive all current logs?',
                'PyRa 4 UI'
            )
        ) {
            await backend.archiveLogs();
            await updateLogs();
        }
    }

    useEffect(() => {
        updateLogs();
    }, []);

    return (
        <div
            className={
                'flex-col w-full h-full pt-4 ' + (props.visible ? 'flex ' : 'hidden ')
            }
        >
            <div className="px-6 mb-4 flex-row-center gap-x-2">
                <Button
                    onClick={() => {
                        updateLogs();
                    }}
                    variant="slate"
                    className="!px-1.5"
                >
                    <div className="w-6 h-6 fill-slate-700 ">{ICONS.refresh}</div>
                </Button>
                <Toggle
                    value={logLevel}
                    setValue={(s: any) => setLogLevel(s)}
                    values={['info', 'debug']}
                />
                <div className="flex-grow" />
                <Button onClick={archiveLogs} variant="red">
                    archive logs
                </Button>
            </div>
            <pre
                className={
                    'w-full !px-6 !py-2 !mb-0 overflow-y-scroll ' +
                    'border-t border-slate-300 bg-white'
                }
            >
                <code className="w-full h-full !text-xs language-log">
                    {logLevel === 'info' ? infoLogs : debugLogs}
                    {(logLevel === 'info' ? infoLogs : debugLogs)
                        .replace('\n', '')
                        .replace(' ', '').length === 0 && (
                        <strong>logs are empty</strong>
                    )}
                </code>
            </pre>
        </div>
    );
}

// TODO: Figure out how to remove the quotes from the logs inside the html -> in order to have syntax highlighting
