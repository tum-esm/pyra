import { useState, useEffect } from 'react';
import { backend, functionalUtils, reduxUtils } from '../utils';
import { customTypes } from '../custom-types';
import { configComponents } from '../components';

const sectionKeys: customTypes.configSectionKey[] = [
    'general',
    'opus',
    'camtracker',
    'error_email',
    'measurement_triggers',
    'tum_plc',
    'vbdsd',
];
export default function ConfigTab(props: { visible: boolean }) {
    const localConfig = reduxUtils.useTypedSelector((s) => s.config.local);
    const configIsDiffering = reduxUtils.useTypedSelector((s) => s.config.isDiffering);
    const dispatch = reduxUtils.useTypedDispatch();

    const setConfigs = (c: customTypes.config | undefined) =>
        dispatch(reduxUtils.configActions.setConfigs(c));
    const resetLocalConfig = () => dispatch(reduxUtils.configActions.resetLocal());

    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const [activeKey, setActiveKey] = useState<customTypes.configSectionKey>('general');
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        loadCentralConfig();
    }, []);

    async function loadCentralConfig() {
        const content = await backend.getConfig();
        try {
            setConfigs(JSON.parse(content.stdout));
        } catch {
            console.log(`Output from get-config: ${content.stdout}`);
        }
    }

    async function saveLocalConfig() {
        if (localConfig !== undefined) {
            setIsSaving(true);
            const parsedLocalConfig = functionalUtils.parseNumberTypes(localConfig);
            let result = await backend.updateConfig(parsedLocalConfig);

            if (result.stdout.includes('Updated config file')) {
                setConfigs(parsedLocalConfig);
                setIsSaving(false);
            } else {
                setErrorMessage(result.stdout);
                setIsSaving(false);
            }
        }
    }

    if ([localConfig, configIsDiffering].includes(undefined)) {
        return <></>;
    }

    return (
        <div className={'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')}>
            <div
                className={
                    'bg-white border-r border-slate-300 shadow ' + 'flex flex-col py-3 z-10 w-44'
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
                                (key1 === activeKey ? 'bg-blue-400 ' : 'bg-transparent')
                            }
                        />
                    </button>
                ))}
            </div>
            <div
                className={
                    'z-0 flex-grow h-full p-6 overflow-y-scroll ' + 'flex-col-left relative pb-20'
                }
            >
                {activeKey === 'general' && <configComponents.ConfigSectionGeneral />}
                {activeKey === 'opus' && <configComponents.ConfigSectionOpus />}
                {activeKey === 'camtracker' && <configComponents.ConfigSectionCamtracker />}
                {activeKey === 'error_email' && <configComponents.ConfigSectionErrorEmail />}
                {activeKey === 'measurement_triggers' && (
                    <configComponents.ConfigSectionMeasurementTriggers />
                )}
                {activeKey === 'tum_plc' && <configComponents.ConfigSectionTumPlc />}
                {activeKey === 'vbdsd' && <configComponents.ConfigSectionVbdsd />}
                {configIsDiffering && (
                    <configComponents.SavingOverlay
                        {...{
                            errorMessage,
                            saveLocalConfig,
                            resetLocalConfig,
                            isSaving,
                        }}
                    />
                )}
            </div>
        </div>
    );
}
