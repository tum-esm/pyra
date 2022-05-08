import React from 'react';
import TextInput from '../essential/text-input';
import Button from '../essential/button';
import LabeledRow from './labeled-row';
import PreviousValue from '../essential/previous-value';

export default function ConfigElementText(props: {
    key1: string;
    key2: string;
    value: string | number;
    oldValue: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
}) {
    const { key1, key2, value, oldValue, setValue, disabled } = props;

    async function triggerFileSelection() {
        const result = await window.electron.selectPath();
        if (result !== undefined && result.length > 0) {
            setValue(result[0]);
        }
    }

    const showfileSelector = key2.endsWith('_path');

    return (
        <LabeledRow key2={key2} modified={value !== oldValue}>
            <div className='relative flex w-full gap-x-1'>
                <TextInput value={value} setValue={setValue} />
                {showfileSelector && !disabled && (
                    <Button variant='blue' onClick={triggerFileSelection}>
                        choose path
                    </Button>
                )}
            </div>
            <PreviousValue
                previousValue={value !== oldValue ? `${oldValue}` : undefined}
            />
        </LabeledRow>
    );
}
