import React from 'react';
import Toggle from '../essential/toggle';
import sortConfigKeys from '../../utils/sort-config-keys';
import ConfigElement from './config-element';
import TextInput from '../essential/text-input';
import capitalizeConfigKey from '../../utils/capitalize-config-key';
import PreviousValue from '../essential/previous-value';

function IntArrayRow(props: {
    label: string;
    value: any;
    oldValue: any;
    setValue(v: any): void;
    disabled?: boolean;
}) {
    const { label, value, oldValue, setValue, disabled } = props;

    const setNumber = (index: number) => (v: string | number) => {
        let newValue = [...value];
        newValue[index] = v;
        setValue(newValue);
    };

    const hasBeenModified = JSON.stringify(value) !== JSON.stringify(oldValue);

    return (
        <div className='relative w-full flex-row-left gap-x-1'>
            <label className='pl-3 overflow-hidden text-sm text-left w-44 opacity-80 text-slate-800 whitespace-nowrap'>
                ↦ {capitalizeConfigKey(label)}:
            </label>
            {hasBeenModified && (
                <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
            )}
            {typeof value === 'object' && (
                <>
                    {value.map((v: number, i: number) => (
                        <TextInput
                            key={i}
                            value={v}
                            disabled={disabled}
                            setValue={setNumber(i)}
                            small
                        />
                    ))}
                    <PreviousValue
                        previousValue={hasBeenModified ? oldValue : undefined}
                    />
                </>
            )}
            {typeof value === 'boolean' && (
                <>
                    <Toggle
                        value={value}
                        setValue={setValue}
                        trueLabel='consider'
                        falseLabel='ignore'
                    />
                    <PreviousValue
                        previousValue={
                            hasBeenModified
                                ? oldValue
                                    ? 'consider'
                                    : 'ignore'
                                : undefined
                        }
                    />
                </>
            )}
        </div>
    );
}

export default function ConfigElementMatrix(props: {
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
        <ConfigElement label={label}>
            {sortConfigKeys(value).map(key => (
                <IntArrayRow
                    key={key}
                    label={key}
                    value={value[key]}
                    oldValue={oldValue[key]}
                    setValue={setArray(key)}
                />
            ))}
        </ConfigElement>
    );
}
