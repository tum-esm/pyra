import React from 'react';

type ShortKey = 'GUI' | 'CLI';
const translations: Record<ShortKey, string> = {
    GUI: 'Graphical User Interface',
    CLI: 'Command Line Interface',
};

export default function Abbreviation(props: { short: ShortKey }): JSX.Element {
    return (
        <span className='tw-relative tw-bg-gray-200 tw-px-1 tw-py-0.5 -tw-my-0.5 tw-rounded tw-font-medium tw-group'>
            {props.short}
            <div className='tw-hidden tw-absolute tw-top-6 tw-left-0 tw-bg-gray-900 tw-rounded tw-shadow tw-text-white tw-px-1 tw-text-sm tw-max-w-md tw-whitespace-nowrap group-hover:tw-flex'>
                {translations[props.short]}
            </div>
        </span>
    );
}
