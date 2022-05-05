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
                    <TextInputRow
                        label='camtracker.config_path'
                        value={localJSON.camtracker.config_path}
                        oldValue={centralJSON.camtracker.config_path}
                        setValue={v =>
                            addLocalUpdate({ camtracker: { config_path: v } })
                        }
                        showfileSelector
                    />
                    <TextInputRow
                        label='camtracker.executable_path'
                        value={localJSON.camtracker.executable_path}
                        oldValue={centralJSON.camtracker.executable_path}
                        setValue={v =>
                            addLocalUpdate({
                                camtracker: { executable_path: v },
                            })
                        }
                        showfileSelector
                    />
                    <TextInputRow
                        label='camtracker.learn_az_elev_path'
                        value={localJSON.camtracker.learn_az_elev_path}
                        oldValue={centralJSON.camtracker.learn_az_elev_path}
                        setValue={v =>
                            addLocalUpdate({
                                camtracker: { learn_az_elev_path: v },
                            })
                        }
                        showfileSelector
                    />
                    <TextInputRow
                        label='camtracker.sun_intensity_path'
                        value={localJSON.camtracker.sun_intensity_path}
                        oldValue={centralJSON.camtracker.sun_intensity_path}
                        setValue={v =>
                            addLocalUpdate({
                                camtracker: { sun_intensity_path: v },
                            })
                        }
                        showfileSelector
                    />
                    <Divider />
                    <TextInputRow
                        label='em27.ip'
                        value={localJSON.em27.ip}
                        oldValue={centralJSON.em27.ip}
                        setValue={v =>
                            addLocalUpdate({
                                em27: { ip: v },
                            })
                        }
                    />
                    <Divider />
                    <ToggleRow
                        label='enclosure.tum_enclosure_is_present'
                        value={localJSON.enclosure.tum_enclosure_is_present}
                        oldValue={
                            centralJSON.enclosure.tum_enclosure_is_present
                        }
                        setValue={v =>
                            addLocalUpdate({
                                enclosure: { tum_enclosure_is_present: v },
                            })
                        }
                    />
                    <Divider />
                    <TextInputRow
                        label='opus.executable_path'
                        value={localJSON.opus.executable_path}
                        oldValue={centralJSON.opus.executable_path}
                        setValue={v =>
                            addLocalUpdate({
                                opus: { executable_path: v },
                            })
                        }
                        showfileSelector
                    />
                    <Divider />
                    <IntArrayInputRow
                        label='plc.actors.current_angle'
                        value={localJSON.plc.actors.current_angle}
                        oldValue={centralJSON.plc.actors.current_angle}
                        setValue={v =>
                            addLocalUpdate({
                                plc: { actors: { current_angle: v } },
                            })
                        }
                    />
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
