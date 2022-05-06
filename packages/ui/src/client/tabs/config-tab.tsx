import React, { useState, useEffect } from 'react';
import TYPES from '../../types/index';
import Divider from '../components/divider';
import ConfigSection from '../components/config-section';
import SavingOverlay from '../components/saving-overlay';
import { defaultsDeep, trim } from 'lodash';

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

export default function ConfigTab(props: { type: 'setup' | 'parameters' }) {
    const [centralJSON, setCentralJSON] = useState<TYPES.configJSON>(undefined);
    const [localJSON, setLocalJSON] = useState<TYPES.configJSON>(undefined);
    const [errorMessage, setErrorMessage] = useState<string>(undefined);

    async function loadCentralJSON() {
        const readConfigFunction =
            props.type === 'setup'
                ? window.electron.readSetupJSON
                : window.electron.readParametersJSON;
        const content = await readConfigFunction();
        setCentralJSON(content);
        setLocalJSON(content);
    }

    useEffect(() => {
        loadCentralJSON();
    }, []);

    async function saveLocalJSON() {
        const saveConfigFunction =
            props.type === 'setup'
                ? window.electron.saveSetupJSON
                : window.electron.saveParametersJSON;
        let result = await saveConfigFunction(localJSON);

        if (
            ['Updated setup file', 'Updated parameters file'].includes(
                trim(result, '\n ')
            )
        ) {
            setCentralJSON(localJSON);
        } else {
            setErrorMessage(result);
        }
    }

    function restoreCentralJSON() {
        setLocalJSON(centralJSON);
    }

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

    return (
        <div className='flex flex-col items-start justify-start w-full h-full p-6 overflow-y-scroll gap-y-5'>
            {localJSON !== undefined && (
                <>
                    {Object.keys(centralJSON).map((key1: string, i: number) => (
                        <React.Fragment key={key1}>
                            {i !== 0 && <Divider />}
                            <ConfigSection
                                {...{
                                    key1,
                                    localJSON,
                                    centralJSON,
                                    addLocalUpdate,
                                }}
                            />
                        </React.Fragment>
                    ))}
                </>
            )}
            {configIsDiffering && (
                <SavingOverlay
                    {...{ errorMessage, saveLocalJSON, restoreCentralJSON }}
                />
            )}
        </div>
    );
}
