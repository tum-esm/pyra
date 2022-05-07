import React from 'react';

export default function TextInput(props: {
    value: string | number;
    setValue(v: string | number): void;
    disabled?: boolean;
    small?: boolean;
}) {
    function setValue(v: string) {
        if (typeof props.value === 'number') {
            let newNumber = parseFloat(v);
            props.setValue(isNaN(newNumber) ? 0 : newNumber);
        } else {
            props.setValue(v);
        }
    }

    return (
        <input
            value={props.value}
            onChange={e => setValue(e.target.value)}
            className={
                'border shadow-sm px-2 rounded ' +
                'font-medium whitespace-nowrap ' +
                'focus:ring-1 focus:outline-none focus:ring-blue-500 ' +
                'border border-gray-300 focus:border-blue-500 shadow-sm ' +
                (props.disabled
                    ? 'bg-slate-200 text-slate-600 '
                    : 'bg-white text-slate-700 ') +
                (props.small
                    ? 'w-12 text-center text-xs h-6 '
                    : 'flex-grow h-8 text-sm ')
            }
        />
    );
}
