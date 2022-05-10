import React from 'react';

export default function Button(props: {
    children: React.ReactNode;
    onClick(): void;
    variant: 'green' | 'red' | 'blue' | 'gray' | 'toggle-active' | 'toggle-inactive';
    disabled?: boolean;
    className?: string;
}) {
    const { children, onClick, variant, className } = props;

    let colorClasses: string = '';
    switch (variant) {
        case 'gray':
            colorClasses =
                'text-gray-800 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border-gray-500/70 ';
            break;
        case 'green':
            colorClasses =
                'text-green-800 bg-green-100 hover:bg-green-200 hover:text-green-900 border-green-500/70 ';
            break;
        case 'red':
            colorClasses =
                'text-red-800 bg-red-100 hover:bg-red-200 hover:text-red-900 border-red-300 ';
            break;
        case 'blue':
            colorClasses =
                'text-blue-900 bg-blue-75 hover:bg-blue-200 hover:text-blue-950 border-blue-300 ';
            break;
        case 'toggle-active':
            colorClasses = 'text-blue-950 bg-blue-300 border-blue-500 z-10 ';
            break;
        case 'toggle-inactive':
            colorClasses =
                'text-gray-450 bg-gray-50 hover:bg-gray-200 hover:text-gray-800 border-gray-300 z-0 ';
            break;
    }
    return (
        <button
            type="button"
            onClick={onClick}
            className={
                'inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-9 border-collapse focus:z-20 whitespace-nowrap ' +
                colorClasses +
                (variant.startsWith('navigation') ? ' ' : 'shadow-sm ') +
                className
            }
        >
            {children}
        </button>
    );
}
