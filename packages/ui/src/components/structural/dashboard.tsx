import { useEffect, useState } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from '../../tabs';
import { structuralComponents } from '../../components';
import { customTypes } from '../../custom-types';
import { diff } from 'deep-diff';
import { dialog } from '@tauri-apps/api';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [initialFetchTriggered, setInitialFetchTriggered] = useState(false);

    const dispatch = reduxUtils.useTypedDispatch();
    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;

    const fetchLogUpdates = reduxUtils.useTypedSelector((s) => s.logs.fetchUpdates);

    useEffect(() => {
        async function fetchStateFile() {
            const fileContent = await fetchUtils.getFileContent('runtime-data/state.json');
            dispatch(reduxUtils.coreStateActions.set(JSON.parse(fileContent)));
        }

        async function fetchLogFile() {
            if (fetchLogUpdates) {
                const fileContent = await fetchUtils.getFileContent('logs/debug.log');
                dispatch(reduxUtils.logsActions.set(fileContent.split('\n')));
            }
        }

        if (!initialFetchTriggered) {
            fetchStateFile();
            fetchLogFile();
            setInitialFetchTriggered(true);
        }

        const interval1 = setInterval(fetchStateFile, 5000);
        const interval2 = setInterval(fetchLogFile, 5000);

        return () => {
            clearInterval(interval1);
            clearInterval(interval2);
        };
    }, [dispatch, fetchLogUpdates, initialFetchTriggered]);

    useEffect(() => {
        async function fetchConfigFile() {
            const fileContent = await fetchUtils.getFileContent('config/config.json');
            const newCentralConfig: customTypes.config = JSON.parse(fileContent);
            const diffsToCentral = diff(centralConfig, newCentralConfig) || [];

            // measurement_decision.cli_decision_result is allowed to change
            // changing any other property from somewhere else than the UI requires
            // a reload of the window
            const reloadIsRequired =
                diffsToCentral.filter(
                    (d) =>
                        d.kind === 'E' &&
                        d.path?.join('.') !== 'measurement_decision.cli_decision_result'
                ).length > 0;

            if (reloadIsRequired) {
                dialog
                    .message('The config.json file has been modified. Reload required', 'PyRa 4 UI')
                    .then(() => window.location.reload());
            } else {
                dispatch(
                    reduxUtils.configActions.setConfigsPartial({
                        measurement_decision: {
                            cli_decision_result:
                                newCentralConfig.measurement_decision.cli_decision_result,
                        },
                    })
                );
            }
        }

        const interval3 = setInterval(fetchConfigFile, 5000);

        return () => {
            clearInterval(interval3);
        };
    }, [dispatch, centralConfig]);

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            <structuralComponents.Header
                {...{
                    tabs: [...tabs, ...(enclosureControlsIsVisible ? ['PLC Controls'] : [])],
                    activeTab,
                    setActiveTab,
                }}
            />
            <main
                className={
                    'flex-grow w-full bg-gray-75 ' + 'h-[calc(200vh-1.5rem)] overflow-y-auto'
                }
            >
                {[
                    ['Overview', <OverviewTab />],
                    ['Automation', <AutomationTab />],
                    ['Configuration', <ConfigurationTab />],
                    ['Logs', <LogTab />],
                ].map((t: any, i) => (
                    <div key={i} className={activeTab === t[0] ? '' : 'hidden'}>
                        {t[1]}
                    </div>
                ))}
                {enclosureControlsIsVisible && (
                    <div className={activeTab === 'PLC Controls' ? '' : 'hidden'}>
                        <ControlTab />
                    </div>
                )}
            </main>
            <structuralComponents.MessageQueue />
        </div>
    );
}
