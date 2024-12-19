import React, { useState, JSX } from 'react';
import { customTypes } from '../custom-types';
import { configurationComponents } from '../components';
import toast from 'react-hot-toast';
import {
    Icon,
    IconAdjustmentsFilled,
    IconCpu,
    IconFileUpload,
    IconMail,
    IconMicroscope,
    IconProps,
    IconSettings,
    IconSunFilled,
} from '@tabler/icons-react';
import { Button } from '../components/ui/button';
import { configSchema, useConfigStore } from '../utils/zustand-utils/config-zustand';
import fetchUtils from '../utils/fetch-utils';
import { join, omit, takeWhile, pick } from 'lodash';
import { ChildProcess } from '@tauri-apps/plugin-shell';
import { getDiff } from 'recursive-diff';

const sections: {
    key: customTypes.configSectionKey;
    label: string;
    icon: React.ForwardRefExoticComponent<IconProps & React.RefAttributes<Icon>>;
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
    icon: React.ForwardRefExoticComponent<IconProps & React.RefAttributes<Icon>>;
}[] = [
    { key: 'tum_enclosure', label: 'TUM Enclosure', icon: IconCpu },
    { key: 'helios', label: 'Helios', icon: IconCpu },
];

export default function ConfigurationTab() {
    const [activeKey, setActiveKey] = useState<customTypes.configSectionKey>('general');
    const { centralConfig, localConfig, setConfig, configIsDiffering } = useConfigStore();
    const { commandIsRunning, runPromisingCommand } = fetchUtils.useCommand();
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);

    function onRevert() {
        setErrorMessage(undefined);
        setConfig(centralConfig);
    }

    async function onSave() {
        if (centralConfig !== undefined && localConfig !== undefined) {
            const parsedLocalConfig = configSchema.parse(localConfig);
            const updatedPaths: string[] = [];
            getDiff(
                omit(parsedLocalConfig, 'measurement_decision.cli_decision_result'),
                omit(centralConfig, 'measurement_decision.cli_decision_result')
            ).forEach((d) => {
                updatedPaths.push(
                    join(
                        takeWhile(d.path, (p) => typeof p === 'string'),
                        '.'
                    )
                );
            });
            runPromisingCommand({
                command: () =>
                    fetchUtils.backend.updateConfig(pick(parsedLocalConfig, updatedPaths)),
                label: 'saving config',
                successLabel: 'saved config',
                onSuccess: () => {
                    setErrorMessage(undefined);
                    setConfig(parsedLocalConfig);
                },
                onError: (p: ChildProcess<string>) => {
                    setErrorMessage(p.stdout);
                },
            });
        }
    }

    function copyConfigFile() {
        if (configIsDiffering()) {
            toast.error('Please save your changes before copying the config file');
        } else if (centralConfig !== undefined) {
            navigator.clipboard.writeText(JSON.stringify(centralConfig, null, 4));
            toast.success('Copied config.json to clipboard');
        } else {
            toast.error('Could not copy config.json to clipboard');
        }
    }

    const SectionButton = (props: {
        section: {
            key: customTypes.configSectionKey;
            label: string;
            icon: React.ForwardRefExoticComponent<IconProps & React.RefAttributes<Icon>>;
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
                <div className="flex-grow" />

                <Button className="mx-2 my-1" onClick={copyConfigFile}>
                    Copy config.json
                </Button>
            </div>
            <div
                className={
                    'z-0 flex-grow h-full p-6 overflow-y-auto relative pb-20 flex flex-col gap-y-2'
                }
            >
                {activeKey === 'general' && <configurationComponents.ConfigSectionGeneral />}
                {activeKey === 'opus' && <configurationComponents.ConfigSectionOpus />}
                {activeKey === 'camtracker' && <configurationComponents.ConfigSectionCamtracker />}
                {activeKey === 'error_email' && <configurationComponents.ConfigSectionErrorEmail />}
                {activeKey === 'measurement_triggers' && (
                    <configurationComponents.ConfigSectionMeasurementTriggers />
                )}
                {activeKey === 'tum_enclosure' && (
                    <configurationComponents.ConfigSectionTUMEnclosure />
                )}
                {activeKey === 'helios' && <configurationComponents.ConfigSectionHelios />}
                {activeKey === 'upload' && <configurationComponents.ConfigSectionUpload />}
                {configIsDiffering() && (
                    <configurationComponents.SavingOverlay
                        {...{
                            errorMessage,
                            onSave,
                            onRevert,
                            isSaving: commandIsRunning,
                        }}
                    />
                )}
            </div>
        </div>
    );
}
