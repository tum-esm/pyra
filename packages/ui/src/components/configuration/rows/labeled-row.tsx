import React from 'react';
import { functionalUtils } from '../../../utils';

export default function LabeledRow(props: {
    key2: string;
    key3?: string;
    modified?: boolean;
    children: React.ReactNode;
}) {
    const { key2, key3, modified, children } = props;

    return (
        <div className="relative flex mb-6">
            <label className="overflow-hidden text-sm text-left w-[12.5rem] text-slate-700 whitespace-nowrap flex-shrink-0 h-9 leading-9">
                <strong>{functionalUtils.capitalizeConfigKey(key2)}</strong>
                {key3 !== undefined && '.' + functionalUtils.capitalizeConfigKey(key3)}
            </label>
            <div className="flex-grow space-y-1 flex-col-left">{children}</div>
            {modified && (
                <div className="absolute top-0 -left-1 w-1.5 h-full -translate-x-2.5 bg-yellow-400 rounded-sm" />
            )}
        </div>
    );
}
