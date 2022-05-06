import React from 'react';
import { initial, last, isNaN } from 'lodash';

function IntArrayRow(props: {
    label: string;
    value: number[];
    oldValue: number[];
    setValue(v: number[]): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    const setNumber = (index: number, v: string) => {
        let newValue = [...value];
        let newNumber = parseInt(v);
        newValue[index] = isNaN(newNumber) ? 0 : newNumber;
        setValue(newValue);
    };

    const hasBeenModified = JSON.stringify(value) !== JSON.stringify(oldValue);

    return (
        <div className='relative w-full flex-row-left gap-x-2'>
            <label className='pl-3 overflow-hidden text-sm text-left w-44 opacity-80 text-slate-800 whitespace-nowrap'>
                ↦ {label}:
            </label>
            {value.map((v, i) => (
                <input
                    key={i}
                    disabled={disabled !== undefined ? disabled : false}
                    value={v}
                    className={
                        'relative z-0 w-12 px-1.5 py-1 font-mono text-xs rounded text-center ' +
                        (disabled
                            ? 'bg-slate-200 text-slate-600 '
                            : 'bg-white text-slate-700 ')
                    }
                    onChange={e => setNumber(i, e.target.value)}
                />
            ))}
            {hasBeenModified && (
                <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
            )}
            {hasBeenModified && (
                <span className='ml-1 text-sm font-normal flex-row-left opacity-80 gap-x-1'>
                    previous value:{' '}
                    {oldValue.map((v, i) => (
                        <span
                            key={i}
                            className='rounded bg-slate-300 px-1 py-0.5 text-slate-900 text-xs'
                        >
                            {v}
                        </span>
                    ))}
                </span>
            )}
        </div>
    );
}

export default function IntArrayMatrix(props: {
    label: string;
    value: { [key: string]: number[] };
    oldValue: { [key: string]: number[] };
    setValue(v: { [key: string]: number[] }): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    const setArray = (key: string) => (v: number[]) => {
        setValue({
            ...JSON.parse(JSON.stringify(value)),
            [key]: v,
        });
    };

    return (
        <div className='flex flex-col items-start justify-start w-full gap-y-1'>
            <label className='text-xs opacity-80 text-slate-800'>
                <span className='font-medium uppercase'>
                    {initial(label.split('.')).join('.')}.
                </span>
                <span className='font-bold uppercase'>
                    {last(label.split('.'))}
                </span>
            </label>
            {Object.keys(value).map(key => (
                <IntArrayRow
                    key={key}
                    label={key}
                    value={value[key]}
                    oldValue={oldValue[key]}
                    setValue={setArray(key)}
                />
            ))}
        </div>
    );
}
