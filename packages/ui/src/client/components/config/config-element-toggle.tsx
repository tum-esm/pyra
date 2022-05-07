import React from 'react';
import Toggle from '../essential/toggle';
import ConfigElement from './config-element';

export default function ConfigElementToggle(props: {
    label?: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
}) {
    const { label, value, oldValue, setValue } = props;

    return (
        <ConfigElement
            label={label}
            previousValue={
                value !== oldValue ? (oldValue ? 'yes' : 'no') : undefined
            }
        >
            <Toggle {...{ value, setValue }} />
        </ConfigElement>
    );
}
