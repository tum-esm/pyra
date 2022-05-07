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
            type='text'
            value={props.value}
            onChange={e => setValue(e.target.value)}
            className={
                'shadow-sm rounded-md border-gray-300 ' +
                'focus:ring-blue-500 focus:border-blue-500 ' +
                (props.small
                    ? 'w-12 text-center text-sm h-7 '
                    : 'flex-grow text-sm h-9 ')
            }
        />
    );
}
