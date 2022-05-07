import React from 'react';
import TextInput from './essential/text-input';
import Button from './essential/button';
import ConfigElement from './config-element';

export default function TextInputRow(props: {
    label: string;
    value: string | number;
    oldValue: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    async function triggerFileSelection() {
        const result = await window.electron.selectPath();
        if (result !== undefined && result.length > 0) {
            setValue(result[0]);
        }
    }

    const showfileSelector = label.endsWith('_path');

    return (
        <ConfigElement
            label={label}
            previousValue={value !== oldValue ? oldValue.toString() : undefined}
        >
            <div className='relative flex w-full gap-x-1'>
                <TextInput value={value} setValue={setValue} />
                {showfileSelector && !disabled && (
                    <Button
                        text='choose path'
                        variant='blue'
                        onClick={triggerFileSelection}
                    />
                )}
            </div>
        </ConfigElement>
    );
}
