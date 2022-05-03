import React from 'react';
import { initial, last } from 'lodash';

export default function TextInputRow(props: {
    label: string;
    value: string;
    oldValue: string;
    setValue(v: string): void;
    showfileSelector?: boolean;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, showfileSelector, disabled } =
        props;

    async function triggerFileSelection() {
        const result = await window.electron.selectPath();
        if (result !== undefined && result.length > 0) {
            setValue(result[0]);
        }
    }

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            <label className='pb-1 text-xs opacity-80 text-slate-800'>
                <span className='font-medium uppercase'>
                    {initial(label.split('.'))}.
                </span>
                <span className='font-bold uppercase'>
                    {last(label.split('.'))}
                </span>
                {value !== oldValue && (
                    <span className='font-normal opacity-80 ml-1.5'>
                        previous value:{' '}
                        <span className='rounded bg-slate-300 px-1 py-0.5 text-slate-900'>
                            {oldValue}
                        </span>
                    </span>
                )}
            </label>
            <div className='relative flex w-full'>
                <input
                    disabled={disabled !== undefined ? disabled : false}
                    value={value}
                    className={
                        'relative z-0 flex-grow px-3 py-1.5 font-mono text-sm ' +
                        'focus:ring-2 focus:outline-none focus:ring-blue-500 ' +
                        (showfileSelector && !disabled
                            ? 'rounded-l focus:rounded-r-sm focus:z-10 '
                            : 'rounded ') +
                        (disabled
                            ? 'bg-slate-200 text-slate-600 '
                            : 'bg-white text-slate-700 ')
                    }
                    onChange={e => setValue(e.target.value)}
                />
                {value !== oldValue && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
                {showfileSelector && !disabled && (
                    <button
                        className={
                            'z-0 relative h-full px-2 rounded-r text-xs ' +
                            'font-medium text-blue-900 bg-blue-50 hover:bg-blue-300 ' +
                            'border-l border-blue-300 focus:border-0 ' +
                            'flex items-center justify-center cursor-pointer ' +
                            'focus:ring-2 focus:outline-none focus:ring-blue-500 focus:z-10 focus:rounded-l-sm '
                        }
                        onClick={triggerFileSelection}
                    >
                        select path
                    </button>
                )}
            </div>
        </div>
    );
}
