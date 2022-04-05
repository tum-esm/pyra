import React from 'react';

export default function TextInputRow(props: {
    label: string;
    value: string;
    oldValue: string;
    setValue(v: string): void;
}) {
    const { label, value, oldValue, setValue } = props;

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            <label className='py-1 text-sm'>
                <span className='font-bold uppercase'>{label}</span>
                {value !== oldValue && (
                    <span className='font-normal opacity-80 ml-1.5'>
                        previous value:{' '}
                        <span className='rounded bg-slate-200 px-1 py-0.5'>
                            {oldValue}
                        </span>
                    </span>
                )}
            </label>
            <input
                value={value}
                className='w-full px-2 py-1 font-mono rounded'
                onChange={e => setValue(e.target.value)}
            />
        </div>
    );
}
