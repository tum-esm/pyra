import React from 'react';
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
    return (
        <>
            {Object.keys(centralJSON[key1]).map((key2: string, j: number) => {
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
                                showfileSelector={key2.endsWith('_path')}
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
            })}
        </>
    );
}
