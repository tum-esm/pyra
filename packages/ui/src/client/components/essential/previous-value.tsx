import React from 'react';

export default function PreviousValue(props: { previousValue?: any }) {
    const { previousValue } = props;
    const sharedClasses1 =
        'ml-1 text-xs font-normal flex-row-left opacity-80 gap-x-1';
    const sharedClasses2 =
        'rounded bg-yellow-150 border border-yellow-400 px-1 py-0 text-yellow-800 text-xs shadow-sm break-all';

    if (typeof previousValue === 'string') {
        return (
            <span className={sharedClasses1}>
                <span className='whitespace-nowrap'>previous value: </span>
                <span className={sharedClasses2}>{previousValue}</span>
            </span>
        );
    } else if (
        typeof previousValue === 'object' &&
        previousValue.length !== undefined
    ) {
        return (
            <span className={sharedClasses1}>
                <span className='whitespace-nowrap'>previous value: </span>
                {previousValue.map((v: any, i: number) => (
                    <span key={i} className={sharedClasses2}>
                        {v}
                    </span>
                ))}
            </span>
        );
    } else {
        return <></>;
    }
}
