import { useState, useEffect } from 'react';
import { defaultsDeep } from 'lodash';

import { backend, functionalUtils } from '../utils';
import TYPES from '../utils/types';
import { configComponents } from '../components';

const sectionKeys: TYPES.configSectionKey[] = [
    'general',
    'opus',
    'camtracker',
    'error_email',
    'measurement_triggers',
    'tum_plc',
    'vbdsd',
];
export default function ConfigTab(props: { visible: boolean }) {
    const [centralConfig, setCentralConfig] = useState<TYPES.config | undefined>(
        undefined
    );
    const [localConfig, setLocalConfig] = useState<TYPES.config | undefined>(undefined);
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const [activeKey, setActiveKey] = useState<TYPES.configSectionKey>('general');

    const [isSaving, setIsSaving] = useState(false);

    async function loadCentralConfig() {
        const content = await backend.getConfig();
        try {
            const newConfig = JSON.parse(content.stdout);
            setCentralConfig(newConfig);
            setLocalConfig(newConfig);
        } catch {
            console.log(`Output from get-config: ${content.stdout}`);
        }
    }

    useEffect(() => {
        loadCentralConfig();
    }, []);

    async function saveLocalConfig() {
        if (localConfig !== undefined) {
            setIsSaving(true);
            const parsedLocalConfig = functionalUtils.parseNumberTypes(localConfig);
            let result = await backend.updateConfig(parsedLocalConfig);

            if (result.stdout.includes('Updated config file')) {
                setLocalConfig(parsedLocalConfig);
                setCentralConfig(parsedLocalConfig);
                setIsSaving(false);
            } else {
                setErrorMessage(result.stdout);
                setIsSaving(false);
            }
        }
    }

    function restoreCentralConfig() {
        setLocalConfig(centralConfig);
    }

    function addLocalUpdate(update: object) {
        const newObject = defaultsDeep(update, JSON.parse(JSON.stringify(localConfig)));
        setLocalConfig(newObject);
        setErrorMessage(undefined);
    }

    const configIsDiffering =
        localConfig !== undefined &&
        centralConfig !== undefined &&
        !functionalUtils.deepEqual(localConfig, centralConfig);

    const sharedSectionProps: any = { localConfig, centralConfig, addLocalUpdate };

    return (
        <div
            className={
                'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')
            }
        >
            {centralConfig !== undefined && localConfig !== undefined && (
                <>
                    <div
                        className={
                            'bg-white border-r border-slate-300 shadow ' +
                            'flex flex-col py-3 z-10 w-44'
                        }
                    >
                        {sectionKeys.map((key1, i) => (
                            <button
                                key={key1}
                                onClick={() => setActiveKey(key1)}
                                className={
                                    'px-6 py-2.5 text-base font-semibold text-left ' +
                                    'flex-row-center gap-x-2 ' +
                                    (key1 === activeKey
                                        ? 'bg-blue-200 text-blue-950 '
                                        : 'text-slate-500 hover:bg-slate-150 hover:text-slate-700 ')
                                }
                            >
                                {functionalUtils.capitalizeConfigKey(key1)}
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
                            'flex-col-left relative pb-20'
                        }
                    >
                        {activeKey === 'general' && (
                            <configComponents.ConfigSectionGeneral
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'opus' && (
                            <configComponents.ConfigSectionOpus
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'camtracker' && (
                            <configComponents.ConfigSectionCamtracker
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'error_email' && (
                            <configComponents.ConfigSectionErrorEmail
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'measurement_triggers' && (
                            <configComponents.ConfigSectionMeasurementTriggers
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'tum_plc' && (
                            <configComponents.ConfigSectionTumPlc
                                {...sharedSectionProps}
                            />
                        )}
                        {activeKey === 'vbdsd' && (
                            <configComponents.ConfigSectionVbdsd
                                {...sharedSectionProps}
                            />
                        )}
                        {configIsDiffering && (
                            <configComponents.SavingOverlay
                                {...{
                                    errorMessage,
                                    saveLocalConfig,
                                    restoreCentralConfig,
                                    isSaving,
                                }}
                            />
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
