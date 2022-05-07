import React, { useState } from 'react';
import ICONS from '../../assets/icons';
import TYPES from '../../../types/index';

import ConfigElementText from './config-element-text';
import ToggleRow from './config-element-toggle';
import IntArrayMatrix from './config-element-matrix';
import sortConfigKeys from '../../utils/sort-config-keys';
import capitalizeConfigKey from '../../utils/capitalize-config-key';

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
                'transition-all duration-100 first:pt-6 last:pb-20 ' +
                (open ? 'bg-gray-50 py-4 ' : 'py-2 ') +
                'first:border-0 border-t border-gray-300'
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
                <h2 className='text-lg font-bold text-gray-900'>
                    {capitalizeConfigKey(key1)}
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
                                    <ConfigElementText {...commonProps} />
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
