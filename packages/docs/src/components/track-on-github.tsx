import React from 'react';

import GitHubLabel from '@site/src/components/github-label';

export default function TrackOnGitHub(props: {
    url: string;
    text: string;
    releaseDate?: string;
}): JSX.Element {
    return (
        <div className='tw-flex tw-gap-x-2 tw-mb-4'>
            <a
                href={props.url}
                className='!tw-no-underline hover:tw-bg-purple-100 tw-p-1 -tw-m-1 tw-rounded !tw-text-purple-700'
            >
                Track <GitHubLabel text={props.text} /> on GitHub
            </a>
            <em>Release Date: {props.releaseDate || 'TBD'}</em>
        </div>
    );
}
