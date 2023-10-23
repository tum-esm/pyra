import React from 'react';
import Spinner from './spinner';

export default function Button(props: {
    children: React.ReactNode;
    onClick(): void;
    variant: 'white' | 'green' | 'red' | 'gray' | 'flat-blue';
    disabled?: boolean;
    className?: string;
    dot?: boolean;
    spinner?: boolean;
}) {
    let { children, onClick, variant, className, spinner, disabled } = props;
    if (spinner) {
        disabled = true;
    }

    let colorClasses: string = '';
    let dotColor: string = ' ';
    switch (variant) {
        case 'white':
            colorClasses = 'elevated-panel text-gray-800 hover:bg-gray-150 hover:text-gray-900 ';
            dotColor = 'bg-gray-300 ';
            break;
        case 'gray':
            colorClasses = 'elevated-panel ';
            if (props.disabled) {
                colorClasses += 'text-gray-400 !bg-gray-100 ';
            } else {
                colorClasses += 'text-gray-700 !bg-gray-75 hover:!bg-gray-200 hover:text-gray-950 ';
            }
            dotColor = 'bg-gray-300 ';
            break;
        case 'green':
            colorClasses = 'elevated-panel text-green-700 hover:bg-green-50 hover:text-green-900 ';
            dotColor = 'bg-green-300 ';
            break;
        case 'red':
            colorClasses = 'elevated-panel text-red-700 hover:bg-red-50 hover:text-red-900 ';
            dotColor = 'bg-red-300 ';
            break;
        case 'flat-blue':
            colorClasses =
                'bg-green-100 rounded-md text-green-800 ' +
                'hover:bg-blue-150 hover:text-blue-950 border border-green-300 ';
            dotColor = 'bg-blue-300 ';
            break;
    }
    return (
        <button
            type="button"
            onClick={props.disabled ? () => {} : onClick}
            className={
                'flex-row-center flex-shrink-0 px-4 h-8 ' +
                'focus:outline-none focus:ring-1 focus:z-20 ' +
                'focus:border-blue-500 focus:ring-blue-500 ' +
                'text-sm whitespace-nowrap text-center font-medium ' +
                'relative ' +
                colorClasses +
                (disabled ? ' cursor-not-allowed ' : ' cursor-pointer ') +
                className
            }
        >
            {props.dot && (
                <div className={'w-2 h-2 mr-1.5 rounded-full flex-shrink-0 ' + dotColor} />
            )}
            {!spinner && children}
            {spinner && <div className="opacity-0">{children}</div>}
            {spinner && (
                <div className="absolute -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
                    <Spinner />
                </div>
            )}
        </button>
    );
}
