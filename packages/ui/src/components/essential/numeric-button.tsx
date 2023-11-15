import { isNaN } from 'lodash';
import React, { useState } from 'react';
import Button from './button';
import TextInput from './text-input';

export default function NumericButton(props: {
    children: React.ReactNode;
    initialValue: number;
    onClick(value: number): void;
    disabled?: boolean;
    className?: string;
    spinner?: boolean;
    postfix?: string;
}) {
    let { children, initialValue, onClick, className, spinner, disabled, postfix } = props;
    if (spinner) {
        disabled = true;
    }

    const [value, setValue] = useState(initialValue);
    return (
        <div className={'flex-row-center gap-x-1 ' + className}>
            <TextInput
                value={value.toString()}
                setValue={(v) => setValue(isNaN(parseInt(v)) ? 0 : parseInt(v))}
                postfix={postfix}
                disabled={props.disabled}
                className="!h-8"
            />
            <Button
                onClick={() => onClick(value)}
                variant="white"
                className="flex-grow"
                disabled={props.disabled}
                spinner={props.spinner}
            >
                {children}
            </Button>
        </div>
    );
}
