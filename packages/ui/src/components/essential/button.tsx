import React from 'react';

export default function Button(props: {
    children: React.ReactNode;
    onClick(): void;
    variant: 'green' | 'red' | 'blue' | 'gray' | 'toggle-active' | 'toggle-inactive';
    disabled?: boolean;
    className?: string;
    dot?: boolean;
}) {
    const { children, onClick, variant, className } = props;

    let colorClasses: string = '';
    let dotColor: string = ' ';
    switch (variant) {
        case 'gray':
            colorClasses =
                'text-gray-800 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 ';
            dotColor = 'bg-gray-300 ';
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
        case 'blue':
            colorClasses =
                'text-blue-900 bg-blue-75 hover:bg-blue-200 hover:text-blue-950 ';
            dotColor = 'bg-blue-300 ';
            break;
        case 'toggle-active':
            colorClasses = 'text-blue-950 bg-blue-300 border-blue-500 z-10 ';
            dotColor = 'bg-blue-300 ';
            break;
        case 'toggle-inactive':
            colorClasses =
                'text-gray-450 bg-gray-50 hover:bg-gray-200 hover:text-gray-800 border-gray-300 z-0 ';
            dotColor = 'bg-gray-100 ';
            break;
    }
    return (
        <button
            type="button"
            onClick={onClick}
            className={
                'flex-row-center px-4 text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-8 border-collapse focus:z-20 whitespace-nowrap text-center flex-shrink-0 ' +
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
