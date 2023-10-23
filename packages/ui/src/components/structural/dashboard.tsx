import { useEffect, useState } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { OverviewTab, ConfigurationTab, LogTab, ControlTab } from '../../tabs';
import { structuralComponents } from '../../components';
import { customTypes } from '../../custom-types';
import { diff } from 'deep-diff';
import { dialog } from '@tauri-apps/api';
import moment from 'moment';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';
import { Toaster } from 'react-hot-toast';

type TabType = 'Overview' | 'Configuration' | 'Logs' | 'PLC Controls';
const tabs: TabType[] = ['Overview', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState<TabType>('Overview');
    const [initialFetchTriggered, setInitialFetchTriggered] = useState(false);

    const dispatch = reduxUtils.useTypedDispatch();
    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;

    const { setLogs } = useLogsStore();

    useEffect(() => {
        async function fetchStateFile() {
            const fileContent = await fetchUtils.getFileContent('runtime-data/state.json');
            dispatch(reduxUtils.coreStateActions.set(JSON.parse(fileContent)));
        }

        async function fetchLogFile() {
            const fileContent = await fetchUtils.getFileContent('logs/debug.log');
            setLogs(fileContent.split('\n'));
        }

        async function fetchActivityFile() {
            const filename = moment().format('YYYY-MM-DD');
            try {
                const fileContent = await fetchUtils.getFileContent(
                    `logs/activity/activity-${filename}.json`
                );
                // @ts-ignore
                dispatch(reduxUtils.activityActions.set(JSON.parse(fileContent)));
            } catch (e) {
                console.debug(`Could not load activity file: ${e}`);
                dispatch(reduxUtils.activityActions.set([]));
            }
        }

        if (!initialFetchTriggered) {
            fetchStateFile();
            fetchLogFile();
            fetchActivityFile();
            setInitialFetchTriggered(true);
        }

        const interval1 = setInterval(fetchStateFile, 5000);
        const interval2 = setInterval(fetchLogFile, 5000);
        const interval3 = setInterval(fetchActivityFile, 5000);

        return () => {
            clearInterval(interval1);
            clearInterval(interval2);
            clearInterval(interval3);
        };
    }, [dispatch, initialFetchTriggered]);

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
                    setActiveTab: (t: any) => setActiveTab(t),
                }}
            />
            <main
                className={
                    'flex-grow w-full bg-gray-50 ' + 'h-[calc(200vh-1.5rem)] overflow-y-auto'
                }
            >
                {[
                    ['Overview', <OverviewTab />],
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
            <Toaster position="bottom-right" />
        </div>
    );
}
