import React, { useEffect, useState } from 'react';
import ICONS from '../assets/icons';
import Button from '../components/button';

export default function LogTab(props: {}) {
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
        <div className='flex flex-col w-full h-full p-6'>
            <div className='flex w-full gap-x-2'>
                <button
                    className={
                        'px-1 py-1 font-medium rounded ' +
                        'bg-white svg-white-button'
                    }
                    onClick={() => {
                        window.electron.playBeep();
                        updateLogs();
                    }}
                >
                    <div className='w-5 h-5'>{ICONS.refresh}</div>
                </button>
                <div className='flex bg-white rounded'>
                    {['info', 'debug'].map((l: 'info' | 'debug', i) => (
                        <button
                            className={
                                'px-3 py-0.5 font-medium rounded-sm ' +
                                'flex items-center gap-x-2 ' +
                                (l === logLevel
                                    ? 'bg-blue-300 text-blue-900 '
                                    : 'bg-slate-100 text-slate-500 ') +
                                (i === 0 ? 'rounded-l ' : '') +
                                (i === 1 ? 'rounded-r ' : '')
                            }
                            onClick={() => setLogLevel(l)}
                        >
                            <div
                                className={
                                    'w-2 h-2 rounded-full ' +
                                    (l === logLevel
                                        ? 'bg-blue-500 '
                                        : 'bg-slate-200 ')
                                }
                            />
                            {l}
                        </button>
                    ))}
                </div>
                <div className='flex-grow' />
                <Button
                    text='Archive Logs'
                    onClick={archiveLogs}
                    variant='red'
                />
            </div>
            <pre className='w-full !px-3 !py-2 !mt-4 !mb-0 bg-white rounded overflow-y-scroll'>
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