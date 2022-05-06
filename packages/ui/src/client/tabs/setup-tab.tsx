import React, { useEffect, useState } from 'react';
import { defaultsDeep } from 'lodash';

import TYPES from '../../types/index';
import Divider from '../components/divider';
import ConfigTab from '../components/config-tab';
import SavingOverlay from '../components/saving-overlay';

export default function SetupTab() {
    const [centralJSON, setCentralJSON] = useState<TYPES.configJSON>(undefined);
    const [localJSON, setLocalJSON] = useState<TYPES.configJSON>(undefined);
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

    return (
        <ConfigTab
            {...{
                localJSON,
                centralJSON,
                addLocalUpdate,
                errorMessage,
                saveLocalJSON,
                restoreCentralJSON,
            }}
        />
    );
}
