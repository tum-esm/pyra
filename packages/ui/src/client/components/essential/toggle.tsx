import React from 'react';
import Button from './button';

export default function Toggle(props: {
    value: boolean;
    setValue(v: boolean): void;
    disabled?: boolean;
    trueLabel?: string;
    falseLabel?: string;
}) {
    const { value, setValue, disabled, trueLabel, falseLabel } = props;

    return (
        <div className='relative flex gap-x-1'>
            <Button
                onClick={() => setValue(true)}
                disabled={disabled}
                variant={value ? 'toggle-active' : 'toggle-inactive'}
            >
                {trueLabel === undefined ? 'yes' : trueLabel}
            </Button>
            <Button
                onClick={() => setValue(false)}
                disabled={disabled}
                variant={value ? 'toggle-inactive' : 'toggle-active'}
            >
                {falseLabel === undefined ? 'no' : falseLabel}
            </Button>
        </div>
    );
}
