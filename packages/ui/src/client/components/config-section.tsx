import React, { useState } from 'react';
import ICONS from '../assets/icons';
import TYPES from '../../types/index';

import TextInputRow from './text-input-row';
import ToggleRow from './toggle-row';
import IntArrayMatrix from './int-array-matrix';
import sortConfigKeys from '../utils/sort-config-keys';

export default function ConfigSection(props: {
    key1: string;
    localJSON: TYPES.configJSON;
    centralJSON: TYPES.configJSON;
    addLocalUpdate(v: TYPES.configJSON): void;
}) {
    const { key1, localJSON, centralJSON, addLocalUpdate } = props;
    const [open, setOpen] = useState(false);

    return (
        <div
            className={
                'flex flex-col w-full gap-y-3 pl-14 pr-6 ' +
                'transition-all duration-100 ' +
                (open ? 'bg-gray-50 py-4 ' : 'py-2 ')
            }
        >
            <div className='w-full -ml-8 flex-row-left gap-x-1'>
                <button
                    className={
                        'w-7 h-7 p-0.5 rounded hover:bg-gray-50 ' +
                        (open ? 'rotate-0 ' : '-rotate-90')
                    }
                    onClick={() => setOpen(!open)}
                >
                    {ICONS.chevronDown}
                </button>
                <h2 className='text-base font-bold text-gray-800'>
                    {key1.toLocaleUpperCase()}
                </h2>
            </div>

            {open &&
                sortConfigKeys(centralJSON[key1]).map(
                    (key2: string, j: number) => {
                        const commonProps = {
                            key: key2,
                            label: key2,
                            value: localJSON[key1][key2],
                            oldValue: centralJSON[key1][key2],
                            setValue: (v: any) =>
                                addLocalUpdate({
                                    [key1]: {
                                        [key2]: v,
                                    },
                                }),
                        };
                        switch (typeof centralJSON[key1][key2]) {
                            case 'string':
                            case 'number':
                                return (
                                    /* @ts-ignore */
                                    <TextInputRow
                                        {...commonProps}
                                        numeric={
                                            typeof centralJSON[key1][key2] ===
                                            'number'
                                        }
                                    />
                                );
                            case 'boolean':
                                return (
                                    /* @ts-ignore */
                                    <ToggleRow {...commonProps} />
                                );
                            case 'object':
                                return (
                                    /* @ts-ignore */
                                    <IntArrayMatrix {...commonProps} />
                                );
                        }
                    }
                )}
        </div>
    );
}
