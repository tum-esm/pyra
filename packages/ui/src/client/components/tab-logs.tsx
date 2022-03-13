import React, { useState } from 'react';

export default function TabLogs(props: {}) {
    const [logLevel, setLogLevel] = useState<'info' | 'debug'>('info');

    async function openFileDialog() {
        const something = await window.electron.showDialog();
    }

    return (
        <div className='flex flex-col w-full h-full p-6'>
            <div className='flex w-full'>
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
                <button
                    className={
                        'px-3 py-0.5 font-medium rounded ' +
                        'bg-red-200 text-red-900'
                    }
                    onClick={openFileDialog}
                >
                    clear logs
                </button>
            </div>
            <pre className='w-full p-3 mt-4 bg-white rounded'>
                <code className='overflow-y-scroll language-log'>
                    {'2022-03-02 14:55:11,061 - pyra.core - INFO - Starting Iteration\n' +
                        '2022-03-02 14:55:17,067 - pyra.core - INFO - Running SystemTimeSync\n' +
                        '2022-03-02 14:55:17,067 - pyra.core - INFO - Running SunTracking'}
                </code>
            </pre>
        </div>
    );
}
