import { useState, useEffect } from 'react';
import TYPES from '../utils/types';
import ConfigSection from '../components/config/config-section';
import SavingOverlay from '../components/config/saving-overlay';
import { defaultsDeep, first, trim } from 'lodash';
import deepEqual from '../utils/deep-equal';
import sortConfigKeys from '../utils/sort-config-keys';
import capitalizeConfigKey from '../utils/capitalize-config-key';
import parseNumberTypes from '../utils/parse-number-types';
import backend from '../utils/backend';

export default function ConfigTab(props: {
    type: 'setup' | 'parameters';
    visible: boolean;
}) {
    const [centralJSON, setCentralJSON] = useState<TYPES.configJSON | undefined>(
        undefined
    );
    const [localJSON, setLocalJSON] = useState<TYPES.configJSON | undefined>(undefined);
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const [activeKey, setActiveKey] = useState<string | undefined>(undefined);

    async function loadCentralJSON() {
        const readConfigFunction =
            props.type === 'setup' ? backend.readSetupJSON : backend.readParametersJSON;
        const content = await readConfigFunction();
        setCentralJSON(content);
        setLocalJSON(content);
        setActiveKey(first(sortConfigKeys(content)));
    }

    useEffect(() => {
        loadCentralJSON();
    }, []);

    async function saveLocalJSON() {
        const saveConfigFunction =
            props.type === 'setup'
                ? backend.updateSetupJSON
                : backend.updateParamtersJSON;
        const parsedLocalJSON = parseNumberTypes(centralJSON, localJSON);
        let result = await saveConfigFunction(parsedLocalJSON);

        if (
            ['Updated setup file', 'Updated parameters file'].includes(
                result.join('\n')
            )
        ) {
            setLocalJSON(parsedLocalJSON);
            setCentralJSON(parsedLocalJSON);
        } else {
            setErrorMessage(result.join(' '));
        }
    }

    function restoreCentralJSON() {
        setLocalJSON(centralJSON);
    }

    function addLocalUpdate(update: object) {
        const newObject = defaultsDeep(update, JSON.parse(JSON.stringify(localJSON)));
        console.log({ newObject });
        setLocalJSON(newObject);
        setErrorMessage(undefined);
    }

    const configIsDiffering =
        localJSON !== undefined &&
        centralJSON !== undefined &&
        !deepEqual(localJSON, centralJSON);

    return (
        <div
            className={
                'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')
            }
        >
            {centralJSON !== undefined && localJSON !== undefined && (
                <>
                    <div
                        className={
                            'bg-white border-r border-gray-300 shadow ' +
                            'flex flex-col py-3 z-10 w-44'
                        }
                    >
                        {sortConfigKeys(centralJSON).map((key1: string, i: number) => (
                            <button
                                key={key1}
                                onClick={() => setActiveKey(key1)}
                                className={
                                    'px-6 py-2.5 text-base font-semibold text-left ' +
                                    'flex-row-center gap-x-2 ' +
                                    (key1 === activeKey
                                        ? 'bg-blue-200 text-blue-950 '
                                        : 'text-gray-500 hover:bg-gray-100 hover:text-gray-600 ')
                                }
                            >
                                {capitalizeConfigKey(key1)}
                                <div className="flex-grow" />
                                <div
                                    className={
                                        'w-2 h-2 bg-blue-400 rounded-full ' +
                                        (key1 === activeKey
                                            ? 'bg-blue-400 '
                                            : 'bg-transparent')
                                    }
                                />
                            </button>
                        ))}
                    </div>
                    <div
                        className={
                            'z-0 flex-grow h-full p-6 overflow-y-scroll ' +
                            'flex-col-left space-y-6 relative pb-20'
                        }
                    >
                        {activeKey !== undefined && (
                            <ConfigSection
                                key0={props.type}
                                key1={activeKey}
                                {...{
                                    localJSON,
                                    centralJSON,
                                    addLocalUpdate,
                                }}
                            />
                        )}
                        {configIsDiffering && (
                            <SavingOverlay
                                {...{
                                    errorMessage,
                                    saveLocalJSON,
                                    restoreCentralJSON,
                                }}
                            />
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
