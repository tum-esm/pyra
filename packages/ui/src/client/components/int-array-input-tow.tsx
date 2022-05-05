import React from 'react';
import { initial, last, values } from 'lodash';

export default function IntArrayInputRow(props: {
    label: string;
    value: number[];
    oldValue: number[];
    setValue(v: number[]): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    const setNumber = (v: string, i: number) => {
        let newValue = [...value];
        newValue[i] = parseInt(v);
        setValue(newValue);
    };

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            <label className='pb-1 text-xs opacity-80 text-slate-800'>
                <span className='font-medium uppercase'>
                    {initial(label.split('.')).join('.')}.
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
            <div className='relative flex w-full gap-x-2'>
                {value.map((v, i) => (
                    <input
                        disabled={disabled !== undefined ? disabled : false}
                        value={v}
                        className={
                            'relative z-0 w-12 px-3 py-1.5 font-mono text-sm rounded text-center ' +
                            (disabled
                                ? 'bg-slate-200 text-slate-600 '
                                : 'bg-white text-slate-700 ')
                        }
                        onChange={e => setNumber(e.target.value, i)}
                    />
                ))}
                {value !== oldValue && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
            </div>
        </div>
    );
}
