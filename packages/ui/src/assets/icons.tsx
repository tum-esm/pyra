import React from 'react';

const SVG = (props: { children: React.ReactNode; id?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id={props.id}>
        {props.children}
    </svg>
);

const ICONS = {
    refresh: (
        <SVG>
            <path
                className="secondary"
                d="M8.52 7.11a5.98 5.98 0 0 1 8.98 2.5 1 1 0 1 1-1.83.8 4 4 0 0 0-5.7-1.86l.74.74A1 1 0 0 1 10 11H7a1 1 0 0 1-1-1V7a1 1 0 0 1 1.7-.7l.82.81zm5.51 8.34l-.74-.74A1 1 0 0 1 14 13h3a1 1 0 0 1 1 1v3a1 1 0 0 1-1.7.7l-.82-.81A5.98 5.98 0 0 1 6.5 14.4a1 1 0 1 1 1.83-.8 4 4 0 0 0 5.7 1.85z"
            />
        </SVG>
    ),
    checkCircle: (
        <SVG>
            <circle cx="12" cy="12" r="10" className="primary" />
            <path
                className="secondary"
                d="M10 14.59l6.3-6.3a1 1 0 0 1 1.4 1.42l-7 7a1 1 0 0 1-1.4 0l-3-3a1 1 0 0 1 1.4-1.42l2.3 2.3z"
            />
        </SVG>
    ),
    chevronDown: (
        <SVG>
            <path
                className="secondary"
                fillRule="evenodd"
                d="M15.3 10.3a1 1 0 0 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 1.4-1.4l3.3 3.29 3.3-3.3z"
            />
        </SVG>
    ),
    info: (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            className="icon icon-tabler icon-tabler-info-square"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            <desc>
                Download more icon variants from https://tabler-icons.io/i/info-square
            </desc>
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
            <rect x="4" y="4" width="16" height="16" rx="2"></rect>
            <polyline points="11 12 12 12 12 16 13 16"></polyline>
        </svg>
    ),
};

export default ICONS;
