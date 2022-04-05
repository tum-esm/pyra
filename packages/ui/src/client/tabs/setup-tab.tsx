import React, { useEffect, useState } from 'react';
import { defaultsDeep } from 'lodash';

import TYPES from '../../types/index';
import TextInputRow from '../components/text-input-row';

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

    let configIsDiffering = false;
    if (localJSON !== undefined && centralJSON !== undefined) {
        configIsDiffering =
            localJSON.enclosure.tum_enclosure_is_present !==
                centralJSON.enclosure.tum_enclosure_is_present ||
            localJSON.em27.ip !== centralJSON.em27.ip ||
            localJSON.plc.is_present !== centralJSON.plc.is_present ||
            localJSON.plc.ip !== centralJSON.plc.ip ||
            localJSON.camtracker.executable_path !==
                centralJSON.camtracker.executable_path ||
            localJSON.camtracker.learn_az_elev_path !==
                centralJSON.camtracker.learn_az_elev_path ||
            localJSON.camtracker.sun_intensity_path !==
                centralJSON.camtracker.sun_intensity_path ||
            localJSON.camtracker.config_path !==
                centralJSON.camtracker.config_path ||
            localJSON.opus.executable_path !==
                centralJSON.opus.executable_path ||
            localJSON.vbdsd.sensor_is_present !==
                centralJSON.vbdsd.sensor_is_present ||
            localJSON.vbdsd.cam_id !== centralJSON.vbdsd.cam_id ||
            localJSON.vbdsd.image_storage_path !==
                centralJSON.vbdsd.image_storage_path;
    }

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
                    <button className='text-green-700 bg-green-200 rounded'>
                        yes
                    </button>
                    <button className='text-red-700 bg-red-200 rounded'>
                        no
                    </button>
                </div>
            )}
        </div>
    );
}
