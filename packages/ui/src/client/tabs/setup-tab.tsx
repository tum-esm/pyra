import React, { useEffect, useState } from 'react';
import { defaultsDeep } from 'lodash';

import TYPES from '../../types/index';
import TextInputRow from '../components/text-input-row';
import Button from '../components/button';

// TODO: Move this to utils
// I didn't find a built-in version yet
// This code is from https://dmitripavlutin.com/how-to-compare-objects-in-javascript/#4-deep-equality
function deepEqual(object1: any, object2: any) {
    const keys1 = Object.keys(object1);
    const keys2 = Object.keys(object2);
    if (keys1.length !== keys2.length) {
        return false;
    }
    for (const key of keys1) {
        const val1 = object1[key];
        const val2 = object2[key];
        const areObjects = isObject(val1) && isObject(val2);
        if (
            (areObjects && !deepEqual(val1, val2)) ||
            (!areObjects && val1 !== val2)
        ) {
            return false;
        }
    }
    return true;
}
function isObject(object: any) {
    return object != null && typeof object === 'object';
}

export default function SetupTab(props: {}) {
    const [centralJSON, setCentralJSON] = useState<TYPES.setupJSON>(undefined);
    const [localJSON, setLocalJSON] = useState<TYPES.setupJSON>(undefined);

    async function loadCentralJSON() {
        const content = await window.electron.readSetupJSON();
        setCentralJSON(content);
        setLocalJSON(content);
    }

    useEffect(() => {
        loadCentralJSON();
    }, []);

    function addLocalUpdate(update: object) {
        const newObject = defaultsDeep(
            update,
            JSON.parse(JSON.stringify(localJSON))
        );
        console.log({ newObject });
        setLocalJSON(newObject);
    }

    const configIsDiffering =
        localJSON !== undefined &&
        centralJSON !== undefined &&
        !deepEqual(localJSON, centralJSON);

    return (
        <div className='flex flex-col w-full h-full p-6'>
            {localJSON !== undefined && (
                <>
                    <TextInputRow
                        label='em27.ip'
                        value={localJSON.em27.ip}
                        oldValue={centralJSON.em27.ip}
                        setValue={v => addLocalUpdate({ em27: { ip: v } })}
                    />
                </>
            )}
            {configIsDiffering && (
                <div className='absolute bottom-0 left-0 z-50 flex flex-row items-center justify-center w-full px-6 py-2 text-sm font-medium bg-white shadow-lg gap-x-2'>
                    <div>Save changes?</div>
                    <Button text='yes' onClick={() => {}} variant='green' />
                    <Button text='no' onClick={() => {}} variant='red' />
                </div>
            )}
        </div>
    );
}
