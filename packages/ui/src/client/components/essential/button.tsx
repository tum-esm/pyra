import React from 'react';

export default function Button(props: {
    text: string;
    onClick(): void;
    variant: 'green' | 'red' | 'blue';
}) {
    const { text, onClick, variant } = props;

    let colorClasses: string = '';
    switch (variant) {
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
                'text-blue-800 bg-blue-75 hover:bg-blue-200 hover:text-blue-900 border-blue-300 ';
            break;
    }
    return (
        <button
            onClick={onClick}
            className={
                'border shadow-sm px-3 h-8 rounded ' +
                'font-medium whitespace-nowrap text-sm ' +
                'focus:ring-1 focus:outline-none focus:ring-blue-500 ' +
                'border focus:border-blue-500 ' +
                colorClasses
            }
        >
            {text}
        </button>
    );
}
