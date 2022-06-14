import React from 'react';

const SVG = (props: { children: React.ReactNode; id?: string }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        stroke-width="3"
        stroke="currentColor"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        id={props.id}
    >
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        {props.children}
    </svg>
);

const ICONS = {
    refresh: (
        <SVG>
            <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4"></path>
            <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"></path>
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
        <SVG>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
            <rect x="4" y="4" width="16" height="16" rx="2"></rect>
            <polyline points="11 12 12 12 12 16 13 16"></polyline>
        </SVG>
    ),
};

export default ICONS;
