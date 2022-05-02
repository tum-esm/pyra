import React from 'react';
import { initial, last } from 'lodash';

export default function TextInputRow(props: {
    label: string;
    value: string;
    oldValue: string;
    setValue(v: string): void;
    fileSelector?: boolean;
}) {
    const { label, value, oldValue, setValue, fileSelector } = props;

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            <label className='py-1 text-xs opacity-80'>
                <span className='font-medium uppercase'>
                    {initial(label.split('.'))}.
                </span>
                <span className='font-bold uppercase'>
                    {last(label.split('.'))}
                </span>
                {value !== oldValue && (
                    <span className='font-normal opacity-80 ml-1.5'>
                        previous value:{' '}
                        <span className='rounded bg-slate-200 px-1 py-0.5'>
                            {oldValue}
                        </span>
                    </span>
                )}
            </label>
            <div className='relative w-full'>
                <input
                    value={value}
                    className='relative w-full px-2 py-1 font-mono text-sm text-gray-800 rounded'
                    onChange={e => setValue(e.target.value)}
                />
                {value !== oldValue && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
                {fileSelector && (
                    <>
                        <label
                            htmlFor={`file-select-${label}`}
                            className='absolute right-0 px-1.5 h-full text-xs font-bold text-blue-900 -translate-y-1/2 bg-blue-100 rounded-r top-1/2 hover:bg-blue-300 flex items-center justify-center cursor-pointer'
                        >
                            select path
                        </label>
                        <input
                            type='file'
                            className='hidden'
                            id={`file-select-${label}`}
                            onChange={console.log}
                        />
                    </>
                )}
            </div>
        </div>
    );
}
