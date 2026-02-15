import { useEffect, useState } from 'react';
import { fetchUtils } from '../../utils';
import { OverviewTab, ConfigurationTab, LogTab, TUMEnclosureControlTab } from '../../tabs';
import { structuralComponents } from '../../components';
import moment from 'moment';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';
import { useActivityHistoryStore } from '../../utils/zustand-utils/activity-zustand';
import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { ChildProcess } from '@tauri-apps/plugin-shell';
import { useConfigStore, configSchema } from '../../utils/zustand-utils/config-zustand';
import { useCoreProcessStore } from '../../utils/zustand-utils/core-process-zustand';

type TabType = 'Overview' | 'Configuration' | 'Logs' | 'TUM Enclosure' | 'AEMET Enclosure';
const tabs: TabType[] = ['Overview', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState<TabType>('Overview');
    const { setPyraCorePid } = useCoreProcessStore();
    const { centralConfig, setConfig, setConfigItem } = useConfigStore();
    const { setCoreState } = useCoreStateStore();
    const { setLogs, addUiLogLine } = useLogsStore();
    const { setActivityHistory } = useActivityHistoryStore();
    const { runPromisingCommand } = fetchUtils.useCommand();

    const TUMEnclosureControlsIsVisible =
        centralConfig?.tum_enclosure !== null && centralConfig?.tum_enclosure !== undefined;

    const AEMETEnclosureControlsIsVisible =
        centralConfig?.aemet_enclosure !== null &&
        centralConfig?.aemet_enclosure !== undefined &&
        !TUMEnclosureControlsIsVisible;

    function checkPyraCoreState() {
        runPromisingCommand({
            command: fetchUtils.backend.checkPyraCoreState,
            label: 'checking Pyra Core state',
            successLabel: 'successfully checked Pyra Core state',
            onSuccess: (p: ChildProcess<string>) => {
                if (p.stdout.includes('not running')) {
                    setPyraCorePid(-1);
                } else {
                    setPyraCorePid(parseInt(p.stdout.replace(/[^\d]/g, '')));
                }
            },
        });
    }

    async function fetchConfig() {
        runPromisingCommand({
            command: fetchUtils.backend.getConfig,
            label: 'loading config file',
            successLabel: 'successfully loaded config file',
            onSuccess: (p: ChildProcess<string>) => {
                setConfig(JSON.parse(p.stdout));
            },
        });
    }
    async function fetchStateFile() {
        try {
            const fileContent = await fetchUtils.getFileContent('logs/state.json');
            setCoreState(JSON.parse(fileContent));
        } catch (e) {
            addUiLogLine('Could not load logs/state.json', `${e}`);
        }
    }

    async function fetchLogFile() {
        try {
            const fileContent = await fetchUtils.getFileContent('logs/debug.log');
            setLogs(fileContent.split('\n'));
        } catch (e) {
            addUiLogLine('Could not load logs/debug.log', `${e}`);
        }
    }

    async function fetchActivityFile() {
        const filename = moment().format('YYYY-MM-DD');
        try {
            const fileContent = await fetchUtils.getFileContent(
                `logs/activity/activity-${filename}.json`
            );
            setActivityHistory(JSON.parse(fileContent));
        } catch (e) {
            addUiLogLine(`Could not load logs/activity/activity-${filename}.json`, `${e}`);
            setActivityHistory([]);
        }
    }

    useEffect(() => {
        checkPyraCoreState();
        fetchConfig();
        fetchStateFile();
        fetchLogFile();
        fetchActivityFile();

        const interval1 = setInterval(checkPyraCoreState, 180000);
        const interval2 = setInterval(fetchStateFile, 5000);
        const interval3 = setInterval(fetchLogFile, 5000);
        const interval4 = setInterval(fetchActivityFile, 60000);

        return () => {
            clearInterval(interval1);
            clearInterval(interval2);
            clearInterval(interval3);
            clearInterval(interval4);
        };
    }, []);

    async function fetchCLIDecisionResult() {
        const newConfig = configSchema.parse(
            JSON.parse((await fetchUtils.backend.getConfig()).stdout)
        );
        const newCLIDecisionResult = newConfig.measurement_decision.cli_decision_result;
        setConfigItem('measurement_decision.cli_decision_result', newCLIDecisionResult);
    }

    useEffect(() => {
        const interval = setInterval(fetchCLIDecisionResult, 5000);

        return () => {
            clearInterval(interval);
        };
    }, []);

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            <structuralComponents.Header
                {...{
                    tabs: [
                        ...tabs,
                        ...(TUMEnclosureControlsIsVisible ? ['TUM Enclosure'] : []),
                        ...(AEMETEnclosureControlsIsVisible ? ['AEMET Enclosure'] : []),
                    ],
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
                {TUMEnclosureControlsIsVisible && (
                    <div className={activeTab === 'TUM Enclosure' ? '' : 'hidden'}>
                        <TUMEnclosureControlTab />
                    </div>
                )}
                {AEMETEnclosureControlsIsVisible && (
                    <div className={activeTab === 'AEMET Enclosure' ? '' : 'hidden'}>TODO</div>
                )}
            </main>
        </div>
    );
}
