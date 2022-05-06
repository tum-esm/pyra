import React from 'react';
import TextInput from './essential/text-input';
import Button from './essential/button';

export default function TextInputRow(props: {
    label: string;
    value: string | number;
    oldValue: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
    numeric?: boolean;
}) {
    const { label, value, oldValue, disabled } = props;

    function setValue(v: string) {
        let newValue: string | number = v;
        if (props.numeric) {
            let newNumber = parseInt(v);
            newValue = isNaN(newNumber) ? 0 : newNumber;
        }
        props.setValue(newValue);
    }

    async function triggerFileSelection() {
        const result = await window.electron.selectPath();
        if (result !== undefined && result.length > 0) {
            setValue(result[0]);
        }
    }

    const showfileSelector = label.endsWith('_path');

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            <label className='pb-1 text-xs opacity-80 text-slate-800'>
                <span className='font-medium'>{label}</span>
                {value !== oldValue && (
                    <span className='font-normal opacity-80 ml-1.5'>
                        previous value:{' '}
                        <span className='rounded bg-slate-300 px-1 py-0.5 text-slate-900'>
                            {oldValue}
                        </span>
                    </span>
                )}
            </label>
            <div className='relative flex w-full gap-x-1'>
                <TextInput value={value.toString()} setValue={setValue} />
                {value !== oldValue && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
                {showfileSelector && !disabled && (
                    <Button
                        text='choose path'
                        variant='blue'
                        onClick={triggerFileSelection}
                    />
                )}
            </div>
        </div>
    );
}
