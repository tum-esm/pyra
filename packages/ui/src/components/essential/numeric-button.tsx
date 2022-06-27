import { isNaN } from 'lodash';
import React, { useState } from 'react';
import Spinner from './spinner';
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

    let colorClasses =
        'elevated-panel text-slate-600 !bg-slate-75 hover:!bg-slate-200 hover:text-slate-950 ';
    return (
        <div className={'flex-row-center gap-x-1 ' + className}>
            <TextInput
                value={value.toString()}
                setValue={(v) => setValue(isNaN(parseInt(v)) ? 0 : parseInt(v))}
                postfix={postfix}
                small
            />
            <button
                type="button"
                onClick={() => (props.disabled ? {} : onClick(value))}
                className={
                    'flex-row-center flex-shrink-0 px-4 h-7 ' +
                    'focus:outline-none focus:ring-1 focus:z-20 ' +
                    'focus:border-blue-500 focus:ring-blue-500 ' +
                    'text-sm whitespace-nowrap text-center font-medium ' +
                    'relative flex-grow ' +
                    colorClasses +
                    (disabled ? ' cursor-not-allowed ' : ' cursor-pointer ')
                }
            >
                {!spinner && children}
                {spinner && <div className="opacity-0">{children}</div>}
                {spinner && (
                    <div className="absolute -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
                        <Spinner />
                    </div>
                )}
            </button>
        </div>
    );
}
