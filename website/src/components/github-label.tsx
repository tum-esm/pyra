import React from 'react';

export default function GitHubLabel(props: { text: string }): JSX.Element {
    return (
        <span className='tw-bg-purple-800 tw-text-purple-50 tw-px-2 tw-py-0.5 tw-rounded tw-font-mono tw-text-sm tw-font-bold'>
            {props.text}
        </span>
    );
}
