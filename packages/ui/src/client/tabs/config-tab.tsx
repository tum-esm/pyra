import React, { useState, useEffect } from 'react';
import TYPES from '../../types/index';
import Divider from '../components/divider';
import ConfigSection from '../components/config-section';
import SavingOverlay from '../components/saving-overlay';
import { defaultsDeep, trim } from 'lodash';
import deepEqual from '../utils/deep-equal';
import sortConfigKeys from '../utils/sort-config-keys';

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
                    {sortConfigKeys(centralJSON).map(
                        (key1: string, i: number) => (
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
                        )
                    )}
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
