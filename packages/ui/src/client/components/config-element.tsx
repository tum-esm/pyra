import React from 'react';
import capitalizeConfigKey from '../utils/capitalize-config-key';

export default function ConfigElement(props: {
    label: string;
    previousValue?: string;
    children: React.ReactNode;
}) {
    const { label, previousValue, children } = props;

    const sharedClasses =
        'relative flex flex-col items-start justify-start w-full gap-y-1';
    return (
        <div className={sharedClasses}>
            <label className='pb-1 text-xs opacity-80 text-slate-800'>
                <span className='font-medium'>
                    {capitalizeConfigKey(label)}
                </span>
                {previousValue !== undefined && (
                    <span className='font-normal opacity-80 ml-1.5'>
                        previous value:{' '}
                        <span className='rounded bg-slate-300 px-1 py-0.5 text-slate-900'>
                            {previousValue}
                        </span>
                    </span>
                )}
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
