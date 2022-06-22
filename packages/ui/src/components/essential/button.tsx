import React from 'react';
import ICONS from '../../assets/icons';

export default function Button(props: {
    children: React.ReactNode;
    onClick(): void;
    variant: 'white' | 'green' | 'red' | 'slate';
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
            colorClasses = 'text-slate-800 hover:bg-slate-150 hover:text-slate-900 ';
            dotColor = 'bg-slate-300 ';
            break;
        case 'slate':
            colorClasses =
                'text-slate-600 !bg-slate-150 hover:!bg-slate-200 hover:text-slate-950 ';
            dotColor = 'bg-slate-300 ';
            break;
        case 'green':
            colorClasses = 'text-green-700 hover:bg-green-50 hover:text-green-900 ';
            dotColor = 'bg-green-300 ';
            break;
        case 'red':
            colorClasses = 'text-red-700 hover:bg-red-50 hover:text-red-900 ';
            dotColor = 'bg-red-300 ';
            break;
    }
    return (
        <button
            type="button"
            onClick={props.disabled ? () => {} : onClick}
            className={
                'flex-row-center flex-shrink-0 px-4 h-7 ' +
                'focus:outline-none focus:ring-1 focus:z-20 ' +
                'focus:border-blue-500 focus:ring-blue-500 ' +
                'text-sm whitespace-nowrap text-center font-medium ' +
                'elevated-panel relative ' +
                colorClasses +
                (disabled ? 'cursor-not-allowed ' : 'cursor-pointer ') +
                className
            }
        >
            {props.dot && (
                <div
                    className={'w-2 h-2 mr-1.5 rounded-full flex-shrink-0 ' + dotColor}
                />
            )}
            {!spinner && children}
            {spinner && <div className="opacity-0">{children}</div>}
            {spinner && (
                <div className="absolute -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
                    <div className="w-4 h-4 animate-spin">{ICONS.spinner}</div>
                </div>
            )}
        </button>
    );
}
