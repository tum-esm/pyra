import { initial, last } from 'lodash';
import React from 'react';
import ICONS from '../assets/icons';

export default function ToggleRow(props: {
    label?: string;
    value: boolean;
    oldValue: boolean;
    setValue(v: boolean): void;
    disabled?: boolean;
    'data-cy'?: string;
    trueLabel?: string;
    falseLabel?: string;
}) {
    const { label, value, oldValue, setValue } = props;

    const sharedClasses = (active: boolean = false) =>
        'min-w-[3rem] pl-2 pr-3 rounded flex-row-center ' +
        'gap-x-1.5 ringable-dark font-weight-600 ' +
        'leading-tight py-1.5 flex-shrink-0 text-sm ' +
        (props.disabled
            ? active
                ? 'text-blue-700 bg-blue-300 cursor-not-allowed '
                : ' text-gray-400 cursor-not-allowed '
            : active
            ? 'text-blue-900 bg-blue-150 '
            : 'text-gray-600 ');

    return (
        <div className='flex flex-col items-start justify-start w-full'>
            {label !== undefined && (
                <label className='pb-1 text-xs opacity-80 text-slate-800'>
                    <span className='font-medium uppercase'>
                        {initial(label.split('.'))}.
                    </span>
                    <span className='font-bold uppercase'>
                        {last(label.split('.'))}
                    </span>
                    {value !== oldValue && (
                        <span className='font-normal opacity-80 ml-1.5'>
                            previous value:{' '}
                            <span className='rounded bg-slate-300 px-1 py-0.5 text-slate-900'>
                                {oldValue ? 'Yes' : 'No'}
                            </span>
                        </span>
                    )}
                </label>
            )}
            <div
                className='relative mt-1 bg-gray-100 rounded flex-row-left gap-x-1'
                data-cy={props['data-cy']}
            >
                {value !== oldValue && label !== undefined && (
                    <div className='absolute top-0 left-0 w-1.5 h-full -translate-x-2.5 bg-blue-500 rounded-sm' />
                )}
                <button
                    className={sharedClasses(value)}
                    onClick={!props.disabled ? () => setValue(true) : () => {}}
                    disabled={props.disabled === true}
                    data-cy={`yes ${value ? 'isactive' : 'isinactive'}`}
                >
                    <div
                        className={`w-4 h-4 flex-shrink-0 ${
                            value ? 'svg-toggle-true' : 'svg-toggle-false'
                        }`}
                    >
                        {ICONS.checkCircle}
                    </div>
                    <div>
                        {props.trueLabel === undefined
                            ? 'Yes'
                            : props.trueLabel}
                    </div>
                </button>
                <button
                    className={sharedClasses(!value)}
                    onClick={!props.disabled ? () => setValue(false) : () => {}}
                    disabled={props.disabled === true}
                    data-cy={`no ${!value ? 'isactive' : 'isinactive'}`}
                >
                    <div
                        className={`w-4 h-4 flex-shrink-0 ${
                            !value ? 'svg-toggle-true' : 'svg-toggle-false'
                        }`}
                    >
                        {ICONS.checkCircle}
                    </div>
                    <div>
                        {props.falseLabel === undefined
                            ? 'No'
                            : props.falseLabel}
                    </div>
                </button>
            </div>
        </div>
    );
}
