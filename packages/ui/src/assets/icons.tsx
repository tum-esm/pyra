import React from 'react';

const SVG = (props: { children: React.ReactNode; id?: string }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        strokeWidth="2"
        stroke="currentColor"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
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
    info: (
        <SVG>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
            <rect x="4" y="4" width="16" height="16" rx="2"></rect>
            <polyline points="11 12 12 12 12 16 13 16"></polyline>
        </SVG>
    ),
    spinner: (
        <SVG>
            <line x1="12" y1="6" x2="12" y2="3"></line>
            <line x1="16.25" y1="7.75" x2="18.4" y2="5.6"></line>
            <line x1="18" y1="12" x2="21" y2="12"></line>
            <line x1="16.25" y1="16.25" x2="18.4" y2="18.4"></line>
            <line x1="12" y1="18" x2="12" y2="21"></line>
            <line x1="7.75" y1="16.25" x2="5.6" y2="18.4"></line>
            <line x1="6" y1="12" x2="3" y2="12"></line>
            <line x1="7.75" y1="7.75" x2="5.6" y2="5.6"></line>
        </SVG>
    ),
    check: (
        <SVG>
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M9 12l2 2l4 -4"></path>
        </SVG>
    ),
    forbid: (
        <SVG>
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <circle cx="12" cy="12" r="9"></circle>
            <line x1="9" y1="9" x2="15" y2="15"></line>
        </SVG>
    ),
    close: (
        <SVG>
            <circle cx="12" cy="12" r="9" opacity={0}></circle>
            <path d="M10 10l4 4m0 -4l-4 4"></path>
        </SVG>
    ),
    alert: (
        <SVG>
            <path d="M12 9v2m0 4v.01"></path>
            <path d="M5 19h14a2 2 0 0 0 1.84 -2.75l-7.1 -12.25a2 2 0 0 0 -3.5 0l-7.1 12.25a2 2 0 0 0 1.75 2.75"></path>
        </SVG>
    ),
};

export default ICONS;
