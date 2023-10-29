import { useState } from 'react';
import { fetchUtils, functionalUtils, reduxUtils } from '../utils';
import { customTypes } from '../custom-types';
import { configurationComponents } from '../components';
import toast from 'react-hot-toast';
import { diff } from 'deep-diff';
import { set } from 'lodash';
import {
    IconAdjustmentsFilled,
    IconCpu,
    IconFileUpload,
    IconMail,
    IconMicroscope,
    IconSettings,
    IconSunFilled,
    TablerIconsProps,
} from '@tabler/icons-react';

const sections: {
    key: customTypes.configSectionKey;
    label: string;
    icon: (props: TablerIconsProps) => JSX.Element;
}[] = [
    { key: 'general', label: 'General', icon: IconSettings },
    { key: 'opus', label: 'OPUS', icon: IconMicroscope },
    { key: 'camtracker', label: 'CamTracker', icon: IconSunFilled },
    { key: 'error_email', label: 'Error Email', icon: IconMail },
    {
        key: 'measurement_triggers',
        label: 'Triggers',
        icon: IconAdjustmentsFilled,
    },
    { key: 'upload', label: 'Upload', icon: IconFileUpload },
];

const hardwareSections: {
    key: customTypes.configSectionKey;
    label: string;
    icon: (props: TablerIconsProps) => JSX.Element;
}[] = [
    { key: 'tum_plc', label: 'TUM Enclosure', icon: IconCpu },
    { key: 'helios', label: 'Helios', icon: IconCpu },
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

    const SectionButton = (props: {
        section: {
            key: customTypes.configSectionKey;
            label: string;
            icon: (props: TablerIconsProps) => JSX.Element;
        };
    }) => (
        <div
            className={
                'w-full border-r-[3px] px-2 py-1 ' +
                (props.section.key === activeKey ? 'border-slate-950' : 'border-transparent')
            }
        >
            <button
                onClick={() => setActiveKey(props.section.key)}
                className={
                    'px-2.5 py-1.5 w-full text-sm font-medium text-left rounded ' +
                    'flex flex-row items-center justify-start gap-x-2.5 h-8 leading-5 ' +
                    (props.section.key === activeKey
                        ? ' text-black '
                        : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800 ')
                }
            >
                <props.section.icon
                    size={16}
                    className={props.section.key === activeKey ? `` : 'opacity-30'}
                />
                <div>{props.section.label}</div>
            </button>
        </div>
    );

    if ([localConfig, configIsDiffering].includes(undefined)) {
        return <></>;
    }

    return (
        <div className={'w-full h-[calc(100vh-3.5rem)] relative flex flex-row'}>
            <div
                className={
                    'bg-white border-r border-gray-300 flex flex-col py-1 z-10 w-44 h-full flex-shrink-0'
                }
            >
                {sections.map((section) => (
                    <SectionButton key={section.key} section={section} />
                ))}
                <div className="w-full h-px my-1 bg-slate-200 " />
                {hardwareSections.map((section) => (
                    <SectionButton key={section.key} section={section} />
                ))}
            </div>
            <div className={'z-0 flex-grow h-full p-6 overflow-y-auto relative pb-20'}>
                {/*{activeKey === 'general' && <configurationComponents.ConfigSectionGeneral />}
                {activeKey === 'opus' && <configurationComponents.ConfigSectionOpus />}
                {activeKey === 'camtracker' && <configurationComponents.ConfigSectionCamtracker />}
                {activeKey === 'error_email' && <configurationComponents.ConfigSectionErrorEmail />}
                {activeKey === 'measurement_triggers' && (
                    <configurationComponents.ConfigSectionMeasurementTriggers />
                )}
                {activeKey === 'tum_plc' && <configurationComponents.ConfigSectionTumPlc />}
                {activeKey === 'helios' && <configurationComponents.ConfigSectionHelios />}
                {activeKey === 'upload' && <configurationComponents.ConfigSectionUpload />}
                {configIsDiffering && (
                    <configurationComponents.SavingOverlay
                        {...{
                            errorMessage,
                            saveLocalConfig,
                            resetLocalConfig,
                            isSaving,
                        }}
                    />
                    )}*/}
            </div>
        </div>
    );
}
