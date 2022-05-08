import React from 'react';
import PreviousValue from '../essential/previous-value';
import Toggle from '../essential/toggle';
import LabeledRow from './labeled-row';

export default function ConfigElementToggle(props: {
    key1: string;
    key2: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { key1, key2, value, oldValue, setValue } = props;

    return (
        <LabeledRow key2={key2} modified={value !== oldValue}>
            <Toggle {...{ value, setValue }} />
            <PreviousValue
                previousValue={
                    value !== oldValue ? (oldValue ? 'Yes' : 'No') : undefined
                }
            />
        </LabeledRow>
    );
}
