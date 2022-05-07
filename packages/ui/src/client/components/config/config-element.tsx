import React from 'react';
import capitalizeConfigKey from '../../utils/capitalize-config-key';
import PreviousValue from '../essential/previous-value';

export default function ConfigElement(props: {
    label: string;
    previousValue?: string | number[] | number;
    children: React.ReactNode;
}) {
    const { label, previousValue, children } = props;

    const sharedClasses =
        'relative flex flex-col items-start justify-start w-full gap-y-1';
    return (
        <div className={sharedClasses}>
            <label className='text-sm text-gray-800 flex-row-left'>
                <span className='font-semibold'>
                    {capitalizeConfigKey(label)}
                </span>
                <PreviousValue previousValue={previousValue} />
            </label>
            <div className={sharedClasses}>
                {previousValue !== undefined && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
                {children}
            </div>
        </div>
    );
}
