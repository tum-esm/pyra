import React from 'react';

export default function Button(props: {
    text: string;
    onClick(): void;
    variant: 'green' | 'red';
}) {
    const { text, onClick, variant } = props;

    let colorClasses: string = '';
    switch (variant) {
        case 'green':
            colorClasses =
                'text-green-700 bg-green-100 hover:bg-green-200 hover:text-green-900 ';
            break;
        case 'red':
            colorClasses =
                'text-red-700 bg-red-100 hover:bg-red-200 hover:text-red-900 ';
            break;
    }
    return (
        <button
            onClick={onClick}
            className={'px-2 py-0.5  rounded font-medium ' + colorClasses}
        >
            {text}
        </button>
    );
}
