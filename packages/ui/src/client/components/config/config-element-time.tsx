import React from 'react';
import TextInput from '../essential/text-input';
import ConfigElement from './config-element';

export default function ConfigElementTime(props: {
    label: string;
    value: [number, number, number];
    oldValue: [number, number, number];
    setValue(v: [number, number, number]): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    return (
        <ConfigElement
            label={label + ' (h : m : s)'}
            previousValue={
                JSON.stringify(value) !== JSON.stringify(oldValue)
                    ? oldValue
                    : undefined
            }
        >
            <div className='relative flex w-full gap-x-1'>
                <TextInput
                    value={value[0]}
                    setValue={(v: number) => setValue([v, value[1], value[2]])}
                    small
                />
                :
                <TextInput
                    value={value[1]}
                    setValue={(v: number) => setValue([value[0], v, value[2]])}
                    small
                />
                :
                <TextInput
                    value={value[2]}
                    setValue={(v: number) => setValue([value[0], value[1], v])}
                    small
                />
            </div>
        </ConfigElement>
    );
}
