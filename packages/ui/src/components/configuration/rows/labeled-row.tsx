import React from 'react';

export default function LabeledRow(props: {
    title: string;
    modified?: boolean;
    children: React.ReactNode;
}) {
    const { title, modified, children } = props;

    return (
        <div className="relative flex flex-shrink-0 gap-x-2">
            <label
                className={
                    'text-sm text-left w-[12.5rem] flex-shrink-0 h-9 leading-tight font-semibold text-gray-700 flex flex-col items-start justify-start'
                }
            >
                {title}
                {modified && <div className="text-xs font-normal text-blue-400">modified</div>}
            </label>
            <div className="flex-grow space-y-1 flex-col-left">{children}</div>
        </div>
    );
}
