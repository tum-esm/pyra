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
                text={props.trueLabel === undefined ? 'Yes' : props.trueLabel}
                onClick={() => setValue(true)}
                disabled={props.disabled}
                variant={value ? 'toggle-true' : 'toggle-false'}
            />
            <Button
                text={props.falseLabel === undefined ? 'No' : props.falseLabel}
                onClick={() => setValue(false)}
                disabled={props.disabled}
                variant={value ? 'toggle-false' : 'toggle-true'}
            />
        </div>
    );
}
