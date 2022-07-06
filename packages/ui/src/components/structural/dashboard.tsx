import { useEffect, useState } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from '../../tabs';
import { essentialComponents, structuralComponents } from '../../components';
import { customTypes } from '../../custom-types';
import { diff } from 'deep-diff';
import { dialog } from '@tauri-apps/api';
import backend from '../../utils/fetch-utils/backend';
import toast from 'react-hot-toast';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [rawLogFileContent, logFileIsLoading] = fetchUtils.useFileWatcher('logs\\debug.log', 10);
    const [rawCoreStateFileContent, coreStateFileIsLoading] = fetchUtils.useFileWatcher(
        'runtime-data\\state.json',
        10
    );


    const [rawConfigFileContent, _] = fetchUtils.useFileWatcher('config\\config.json', 10);
    const dispatch = reduxUtils.useTypedDispatch();

    // add coreState loading=true to redux when file change has been detected
    useEffect(() => {
        dispatch(reduxUtils.logsActions.setLoading(logFileIsLoading));
    }, [logFileIsLoading]);

    // add coreState loading=true to redux when file change has been detected
    useEffect(() => {
        dispatch(reduxUtils.coreStateActions.setLoading(coreStateFileIsLoading));
    }, [coreStateFileIsLoading]);

    // load logs when logs/debug.log has changed
    useEffect(() => {
        if (rawLogFileContent !== undefined) {
            dispatch(reduxUtils.logsActions.set(rawLogFileContent.split('\n')));
        }
    }, [rawLogFileContent]);

    // load coreState when runtime-data/state.json has changed
    useEffect(() => {
        if (rawCoreStateFileContent !== undefined) {
            dispatch(reduxUtils.coreStateActions.set(JSON.parse(rawCoreStateFileContent)));
        }
    }, [rawCoreStateFileContent]);

    // load config when config/config.json has changed
    // check, whether a reload is required
    useEffect(() => {
        if (rawConfigFileContent !== undefined) {
            const newCentralConfig: customTypes.config = JSON.parse(rawConfigFileContent);
            const diffsToCentral = diff(centralConfig, newCentralConfig);
            if (diffsToCentral === undefined) {
                return;
            }

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
                dispatch(reduxUtils.configActions.setConfigsPartial(newCentralConfig));
            }
        }
    }, [rawConfigFileContent]);

    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;

    // fetch PLC State via CLI when PLC is controlled by user
    useEffect(() => {
        let watchInterval: NodeJS.Timer | undefined = undefined;
        // load stuff directly from PLC if user has set the PLC interaction to manual
        if (centralConfig?.tum_plc?.controlled_by_user) {
            watchInterval = setInterval(async () => {
                dispatch(reduxUtils.coreStateActions.setLoading(true));
                const result = await backend.readFromPLC();
                if (result.code !== 0) {
                    console.error(
                        `Could not fetch core state. processResult = ${JSON.stringify(result)}`
                    );
                    toast.error(
                        `Could not fetch core state, please look in the console for details`
                    );
                } else {
                    try {
                        const newCoreState = JSON.parse(result.stdout);
                        dispatch(reduxUtils.coreStateActions.setPartial({ enclosure_plc_readings: newCoreState }));
                    } catch {
                        toast.error(`Could not fetch core state: ${result.stdout}`);
                    }
                }
                dispatch(reduxUtils.coreStateActions.setLoading(false));
            }, 5000);
        }
        return () => clearInterval(watchInterval);
    }, [centralConfig]);

    const coreStateContent = reduxUtils.useTypedSelector((s) => s.coreState.content);
    const logsAreEmpty = reduxUtils.useTypedSelector((s) => s.logs.empty);
    const initialFileContentsAreLoading =
        coreStateContent === undefined || logsAreEmpty === undefined;

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
                    'flex-grow w-full bg-gray-75 ' + 'h-[calc(200vh-1.5rem)] overflow-y-scroll'
                }
            >
                {initialFileContentsAreLoading && <essentialComponents.Spinner />}
                {!initialFileContentsAreLoading && (
                    <>
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
                    </>
                )}
            </main>
            <structuralComponents.MessageQueue />
        </div>
    );
}
