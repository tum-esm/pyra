import React from 'react';

export default function TextInput(props: {
    value: string;
    setValue(v: string): void;
    disabled?: boolean;
    small?: boolean;
    postfix?: string | undefined;
}) {
    return (
        <div className={'relative ' + (props.small ? '' : 'flex-grow')}>
            <input
                type='text'
                value={props.value}
                onChange={e => props.setValue(e.target.value)}
                className={
                    'shadow-sm rounded-md border-gray-300 text-sm w-full ' +
                    'focus:ring-blue-500 focus:border-blue-500 ' +
                    (props.small ? 'w-12 text-center h-7 ' : 'flex-grow h-9 ')
                }
            />
            {props.postfix !== undefined && (
                <div className='absolute text-sm text-gray-900 -translate-y-[calc(50%-0.5px)] opacity-50 top-1/2 left-3 pointer-events-none'>
                    <span className='opacity-0'>{props.value}</span>{' '}
                    {props.postfix}
                </div>
            )}
        </div>
    );
}
