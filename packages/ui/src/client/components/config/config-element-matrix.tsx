import React from 'react';
import Toggle from '../essential/toggle';
import sortConfigKeys from '../../utils/sort-config-keys';
import TextInput from '../essential/text-input';
import PreviousValue from '../essential/previous-value';
import LabeledRow from './labeled-row';

function IntArrayRow(props: {
    key2: string;
    key3: string;
    value: any;
    oldValue: any;
    setValue(v: any): void;
    disabled?: boolean;
}) {
    const { key2, key3, value, oldValue, setValue, disabled } = props;

    const setNumber = (index: number) => (v: string | number) => {
        let newValue = [...value];
        newValue[index] = v;
        setValue(newValue);
    };

    const hasBeenModified = JSON.stringify(value) !== JSON.stringify(oldValue);

    return (
        <LabeledRow
            key2={key2}
            key3={key3}
            modified={JSON.stringify(value) !== JSON.stringify(oldValue)}
        >
            {typeof value === 'object' && (
                <div className='flex-row-left gap-x-1'>
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
                </div>
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
        </LabeledRow>
    );
}

export default function ConfigElementMatrix(props: {
    key1: string;
    key2: string;
    value: { [key: string]: number[] };
    oldValue: { [key: string]: number[] };
    setValue(v: { [key: string]: number[] }): void;
    disabled?: boolean;
}) {
    const { key1, key2, value, oldValue, setValue, disabled } = props;

    const setArray = (key: string) => (v: number[]) => {
        setValue({
            ...JSON.parse(JSON.stringify(value)),
            [key]: v,
        });
    };

    return (
        <div className='relative flex flex-col items-start justify-start w-full gap-y-1'>
            {sortConfigKeys(value).map(key3 => (
                <IntArrayRow
                    key2={key2}
                    key3={key3}
                    value={value[key3]}
                    oldValue={oldValue[key3]}
                    setValue={setArray(key3)}
                />
            ))}
        </div>
    );
}
