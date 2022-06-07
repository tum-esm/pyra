import React from 'react';

export default function Button(props: {
    children: React.ReactNode;
    onClick(): void;
    variant: 'green' | 'red' | 'blue' | 'slate' | 'toggle-active' | 'toggle-inactive';
    disabled?: boolean;
    className?: string;
    dot?: boolean;
}) {
    const { children, onClick, variant, className } = props;

    let colorClasses: string = '';
    let dotColor: string = ' ';
    switch (variant) {
        case 'slate':
            colorClasses =
                'text-slate-800 bg-white hover:bg-slate-100 hover:text-slate-900 ';
            dotColor = 'bg-slate-300 ';
            break;
        case 'green':
            colorClasses =
                'text-green-700 bg-white hover:bg-green-50 hover:text-green-900 ';
            dotColor = 'bg-green-300 ';
            break;
        case 'red':
            colorClasses = 'text-red-700 bg-white hover:bg-red-50 hover:text-red-900 ';
            dotColor = 'bg-red-300 ';
            break;
    }
    return (
        <button
            type="button"
            onClick={onClick}
            className={
                'flex-row-center flex-shrink-0 px-4 h-7 ' +
                'focus:outline-none focus:ring-1 focus:z-20 ' +
                'focus:border-blue-500 focus:ring-blue-500 ' +
                'text-sm whitespace-nowrap text-center font-medium ' +
                'elevated-panel ' +
                colorClasses +
                className
            }
        >
            {props.dot && (
                <div
                    className={'w-2 h-2 mr-1.5 rounded-full flex-shrink-0 ' + dotColor}
                />
            )}
            {children}
        </button>
    );
}
