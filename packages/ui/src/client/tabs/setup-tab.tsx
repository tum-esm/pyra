import React, { useEffect, useState } from 'react';
import { defaultsDeep } from 'lodash';

import TYPES from '../../types/index';
import TextInputRow from '../components/text-input-row';
import Button from '../components/button';
import Divider from '../components/divider';
import ToggleRow from '../components/toggle-row';
import IntArrayInputRow from '../components/int-array-input-tow';

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
    const [errorMessage, setErrorMessage] = useState<string>(undefined);

    async function loadCentralJSON() {
        const content = await window.electron.readSetupJSON();
        setCentralJSON(content);
        setLocalJSON(content);
    }

    async function saveLocalJSON() {
        const result = await window.electron.saveSetupJSON(
            JSON.stringify(localJSON)
        );
        if (result.includes('Updated setup file')) {
            setCentralJSON(localJSON);
        } else {
            setErrorMessage(result);
        }
    }

    function restoreCentralJSON() {
        setLocalJSON(centralJSON);
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
        setErrorMessage(undefined);
    }

    const configIsDiffering =
        localJSON !== undefined &&
        centralJSON !== undefined &&
        !deepEqual(localJSON, centralJSON);

    /*
    centraljson.keys.map
        divider
        key.keys.map
            textinput OR toggle OR intarraymatrix
    */
    return (
        <div className='flex flex-col items-start justify-start w-full h-full p-6 overflow-y-scroll gap-y-4'>
            {localJSON !== undefined && (
                <>
                    {Object.keys(centralJSON).map((key1: any, i: number) => (
                        <>
                            {i !== 0 && <Divider />}
                            {/* @ts-ignore */}
                            {Object.keys(centralJSON[key1]).map(
                                (key2: string, j: number) => {
                                    const commonProps = {
                                        label: `${key1}.${key2}`,
                                        /* @ts-ignore */
                                        value: localJSON[key1][key2],
                                        /* @ts-ignore */
                                        oldValue: centralJSON[key1][key2],
                                        setValue: (v: any) =>
                                            addLocalUpdate({
                                                [key1]: {
                                                    [key2]: v,
                                                },
                                            }),
                                    };
                                    /* @ts-ignore */
                                    switch (typeof centralJSON[key1][key2]) {
                                        case 'string':
                                            return (
                                                <TextInputRow
                                                    {...commonProps}
                                                    showfileSelector={key2.endsWith(
                                                        '_path'
                                                    )}
                                                />
                                            );
                                        case 'boolean':
                                            return (
                                                <ToggleRow {...commonProps} />
                                            );
                                        case 'object':
                                            return 'array matrix';
                                    }
                                }
                            )}
                        </>
                    ))}
                    {/*
                    <IntArrayInputRow
                        label='plc.actors.current_angle'
                        value={localJSON.plc.actors.current_angle}
                        oldValue={centralJSON.plc.actors.current_angle}
                        setValue={v =>
                            addLocalUpdate({
                                plc: { actors: { current_angle: v } },
                            })
                        }
                    />*/}
                </>
            )}
            {configIsDiffering && (
                <div className='absolute bottom-0 left-0 z-50 flex flex-row items-center justify-center w-full px-6 py-2 text-sm font-medium text-center bg-white shadow-lg gap-x-2'>
                    {errorMessage !== undefined && (
                        <span className='text-red-700'>
                            {errorMessage}
                            <br />
                            <div className='h-1.5' />
                            <Button
                                text='revert changes'
                                onClick={restoreCentralJSON}
                                variant='red'
                            />
                        </span>
                    )}
                    {errorMessage === undefined && (
                        <>
                            <div>Save changes?</div>
                            <Button
                                text='yes'
                                onClick={saveLocalJSON}
                                variant='green'
                            />
                            <Button
                                text='no'
                                onClick={restoreCentralJSON}
                                variant='red'
                            />
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
