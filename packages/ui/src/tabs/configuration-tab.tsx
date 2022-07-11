import { useState } from 'react';
import { fetchUtils, functionalUtils, reduxUtils } from '../utils';
import { customTypes } from '../custom-types';
import { configurationComponents } from '../components';
import toast from 'react-hot-toast';
import { diff } from 'deep-diff';
import { set } from 'lodash';

const sections: { key: customTypes.configSectionKey; label: string }[] = [
    { key: 'general', label: 'General' },
    { key: 'opus', label: 'OPUS' },
    { key: 'camtracker', label: 'CamTracker' },
    { key: 'error_email', label: 'Error Email' },
    { key: 'measurement_triggers', label: 'Triggers' },
    { key: 'tum_plc', label: 'TUM PLC' },
    { key: 'vbdsd', label: 'VBDSD' },
];
export default function ConfigurationTab() {
    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const localConfig = reduxUtils.useTypedSelector((s) => s.config.local);
    const errorMessage = reduxUtils.useTypedSelector((s) => s.config.errorMessage);
    const configIsDiffering = reduxUtils.useTypedSelector((s) => s.config.isDiffering);
    const dispatch = reduxUtils.useTypedDispatch();

    const setConfigs = (c: customTypes.config | undefined) =>
        dispatch(reduxUtils.configActions.setConfigs(c));
    const resetLocalConfig = () => {
        dispatch(reduxUtils.configActions.resetLocal());
        setErrorMessage(undefined);
    };
    const setErrorMessage = (m: string | undefined) =>
        dispatch(reduxUtils.configActions.setErrorMessage(m));

    const [activeKey, setActiveKey] = useState<customTypes.configSectionKey>('general');
    const [isSaving, setIsSaving] = useState(false);

    async function saveLocalConfig() {
        if (localConfig !== undefined) {
            setIsSaving(true);
            const parsedLocalConfig = functionalUtils.parseNumberTypes(localConfig);
            const diffsToCentral = diff(centralConfig, parsedLocalConfig);
            const minimalConfigUpdate = {};
            diffsToCentral?.forEach((d) => {
                if (d.kind === 'E') {
                    set(
                        minimalConfigUpdate,
                        d.path ? d.path.map((x: any) => x.toString()) : [],
                        d.rhs
                    );
                }
            });
            let result = await fetchUtils.backend.updateConfig(minimalConfigUpdate);

            if (result.stdout.includes('Updated config file')) {
                setConfigs(parsedLocalConfig);
            } else if (result.stdout.length !== 0) {
                setErrorMessage(result.stdout);
            } else {
                console.error(
                    `Could not update config file. processResult = ${JSON.stringify(result)}`
                );
                toast.error(`Could not update config file, please look in the console for details`);
            }
            setIsSaving(false);
        }
    }

    if ([localConfig, configIsDiffering].includes(undefined)) {
        return <></>;
    }

    return (
        <div className={'w-full h-[calc(100vh-3.5rem)] relative flex flex-row'}>
            <div
                className={
                    'bg-white border-r border-gray-300 shadow ' +
                    'flex flex-col py-3 z-10 w-44 h-full'
                }
            >
                {sections.map((section) => (
                    <button
                        key={section.key}
                        onClick={() => setActiveKey(section.key)}
                        className={
                            'px-6 py-2.5 text-base font-semibold text-left ' +
                            'flex-row-center gap-x-2 ' +
                            (section.key === activeKey
                                ? 'bg-blue-200 text-blue-950 '
                                : 'text-gray-500 hover:bg-gray-150 hover:text-gray-700 ')
                        }
                    >
                        {section.label}
                        <div className="flex-grow" />
                        <div
                            className={
                                'w-2 h-2 bg-blue-400 rounded-full ' +
                                (section.key === activeKey ? 'bg-blue-400 ' : 'bg-transparent')
                            }
                        />
                    </button>
                ))}
            </div>
            <div className={'z-0 flex-grow h-full p-6 overflow-y-auto relative pb-20'}>
                {activeKey === 'general' && <configurationComponents.ConfigSectionGeneral />}
                {activeKey === 'opus' && <configurationComponents.ConfigSectionOpus />}
                {activeKey === 'camtracker' && <configurationComponents.ConfigSectionCamtracker />}
                {activeKey === 'error_email' && <configurationComponents.ConfigSectionErrorEmail />}
                {activeKey === 'measurement_triggers' && (
                    <configurationComponents.ConfigSectionMeasurementTriggers />
                )}
                {activeKey === 'tum_plc' && <configurationComponents.ConfigSectionTumPlc />}
                {activeKey === 'vbdsd' && <configurationComponents.ConfigSectionVbdsd />}
                {configIsDiffering && (
                    <configurationComponents.SavingOverlay
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
