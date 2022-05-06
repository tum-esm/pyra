import React, { useState } from 'react';
import ICONS from '../assets/icons';
import TYPES from '../../types/index';

import TextInputRow from './text-input-row';
import ToggleRow from './toggle-row';
import IntArrayMatrix from './int-array-matrix';

export default function ConfigSection(props: {
    key1: string;
    localJSON: TYPES.configJSON;
    centralJSON: TYPES.configJSON;
    addLocalUpdate(v: TYPES.configJSON): void;
}) {
    const { key1, localJSON, centralJSON, addLocalUpdate } = props;
    const [open, setOpen] = useState(false);

    return (
        <>
            <div className='w-full flex-row-left gap-x-1'>
                <button
                    className={
                        'w-7 h-7 p-0.5 rounded hover:bg-gray-50 ' +
                        (open ? 'rotate-0 ' : '-rotate-90')
                    }
                    onClick={() => setOpen(!open)}
                >
                    {ICONS.chevronDown}
                </button>
                <h2 className='text-lg font-bold text-gray-800'>
                    {key1.toLocaleUpperCase()}
                </h2>
            </div>

            {open &&
                Object.keys(centralJSON[key1]).map(
                    (key2: string, j: number) => {
                        const commonProps = {
                            key: `${key1}.${key2}`,
                            label: `${key1}.${key2}`,
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
                                return (
                                    /* @ts-ignore */
                                    <TextInputRow
                                        {...commonProps}
                                        showfileSelector={key2.endsWith(
                                            '_path'
                                        )}
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
        </>
    );
}
