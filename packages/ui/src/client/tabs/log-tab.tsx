import React, { useEffect, useState } from 'react';
import Toggle from '../components/essential/toggle';
import ICONS from '../assets/icons';
import Button from '../components/essential/button';

export default function LogTab(props: { visible: boolean }) {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');
    const [infoLogs, setInfoLogs] = useState<string>('');
    const [debugLogs, setDebugLogs] = useState<string>('');

    async function updateLogs() {
        setInfoLogs(
            (await window.electron.readInfoLogs())
                .split('\n')
                .reverse()
                .join('\n')
        );
        setDebugLogs(
            (await window.electron.readDebugLogs())
                .split('\n')
                .reverse()
                .join('\n')
        );
    }

    async function archiveLogs() {
        await window.electron.archiveLogs();
        await updateLogs();
    }

    useEffect(() => {
        updateLogs();
    }, []);

    return (
        <div
            className={
                'flex-col w-full h-full p-6 ' +
                (props.visible ? 'flex ' : 'hidden ')
            }
        >
            <div className='flex-row-center gap-x-2'>
                <Button
                    onClick={() => {
                        window.electron.playBeep();
                        updateLogs();
                    }}
                    variant='gray'
                    className='!px-0.5 !py-1 !h-7 '
                >
                    <div className='w-6 h-6 fill-gray-700 '>
                        {ICONS.refresh}
                    </div>
                </Button>
                <Toggle
                    value={logLevel == 'info'}
                    setValue={v => setLogLevel(v ? 'info' : 'debug')}
                    trueLabel='info'
                    falseLabel='debug'
                />
                <div className='flex-grow' />
                <Button onClick={archiveLogs} variant='red'>
                    archive logs
                </Button>
            </div>
            <pre
                className={
                    'w-full !px-3 !py-2 !mt-4 !mb-0 bg-white rounded overflow-y-scroll ' +
                    'border border-gray-300 shadow-sm'
                }
            >
                <code className='w-full h-full !text-sm language-log'>
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
