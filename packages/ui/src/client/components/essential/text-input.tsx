import React from 'react';

export default function TextInput(props: {
    value: string;
    setValue(v: string): void;
    disabled?: boolean;
}) {
    return (
        <input
            value={props.value}
            onChange={e => props.setValue(e.target.value)}
            className={
                'border shadow-sm px-2 h-8 rounded text-sm ' +
                'font-medium whitespace-nowrap flex-grow ' +
                'focus:ring-1 focus:outline-none focus:ring-blue-500 ' +
                'border border-gray-300 focus:border-blue-500 shadow-sm ' +
                (props.disabled
                    ? 'bg-slate-200 text-slate-600 '
                    : 'bg-white text-slate-700 ')
            }
        />
    );
}
