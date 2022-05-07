import React, { useState } from 'react';
import ICONS from '../../assets/icons';
import TYPES from '../../../types/index';

import ConfigElementText from './config-element-text';
import ConfigElementToggle from './config-element-toggle';
import ConfigElementMatrix from './config-element-matrix';
import ConfigElementTime from './config-element-time';

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
            <button
                className={
                    'pr-2.5 mr-auto -ml-8 rounded flex-row-left gap-x-1 ' +
                    'text-black fill-black ' +
                    'hover:text-green-600 hover:fill-green-600'
                }
                onClick={() => setOpen(!open)}
            >
                <div
                    className={
                        'w-7 h-7 p-0.5 ' + (open ? 'rotate-0 ' : '-rotate-90')
                    }
                >
                    {ICONS.chevronDown}
                </div>
                <div className={'text-base font-bold '}>
                    {capitalizeConfigKey(key1)}
                </div>
            </button>

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
                        const oldValue: any = centralJSON[key1][key2];
                        switch (typeof oldValue) {
                            case 'string':
                            case 'number':
                                return (
                                    /* @ts-ignore */
                                    <ConfigElementText {...commonProps} />
                                );
                            case 'boolean':
                                return (
                                    /* @ts-ignore */
                                    <ConfigElementToggle {...commonProps} />
                                );
                            case 'object':
                                if (oldValue.length === undefined) {
                                    return (
                                        /* @ts-ignore */
                                        <ConfigElementMatrix {...commonProps} />
                                    );
                                } else if (oldValue.length === 3) {
                                    return (
                                        /* @ts-ignore */
                                        <ConfigElementTime {...commonProps} />
                                    );
                                }
                        }
                    }
                )}
        </div>
    );
}
