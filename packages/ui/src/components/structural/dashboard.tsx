import { useEffect, useState } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from '../../tabs';
import { essentialComponents, structuralComponents } from '../../components';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('Overview');

    const [rawLogFileContent, logFileIsLoading] = fetchUtils.useFileWatcher('logs\\debug.log', 2);
    const [rawCoreStateFileContent, coreStateFileIsLoading] = fetchUtils.useFileWatcher(
        'runtime-data\\state.json',
        2
    );
    const [rawConfigFileContent, _] = fetchUtils.useFileWatcher('config\\config.json', 2);

    const dispatch = reduxUtils.useTypedDispatch();

    useEffect(() => {
        dispatch(reduxUtils.logsActions.setLoading(logFileIsLoading));
    }, [logFileIsLoading]);

    useEffect(() => {
        dispatch(reduxUtils.coreStateActions.setLoading(coreStateFileIsLoading));
    }, [coreStateFileIsLoading]);

    useEffect(() => {
        if (rawLogFileContent !== undefined) {
            dispatch(reduxUtils.logsActions.set(rawLogFileContent.split('\n')));
        }
    }, [rawLogFileContent]);

    useEffect(() => {
        if (rawCoreStateFileContent !== undefined) {
            dispatch(reduxUtils.coreStateActions.set(JSON.parse(rawCoreStateFileContent)));
        }
    }, [rawCoreStateFileContent]);

    useEffect(() => {
        if (rawConfigFileContent !== undefined) {
            dispatch(reduxUtils.configActions.setConfigs(JSON.parse(rawConfigFileContent)));
        }
    }, [rawConfigFileContent]);

    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;

    /*
    // TODO: Fetch PLC State via CLI when PLC is controlled by user
    useEffect(() => {
        let watchInterval: NodeJS.Timer | undefined = undefined;
        if (centralConfig !== undefined && pyraCorePID !== undefined) {
            // load stuff directly from PLC if pyraCore is not running
            // or user has set the PLC interaction to manual
            if (!pyraCoreIsRunning || centralConfig.tum_plc?.controlled_by_user === true) {
                watchInterval = setInterval(() => setCoreStateShouldBeLoaded(true), 5000);
            }
        }
        return () => clearInterval(watchInterval);
    }, [coreState, pyraCorePID, centralConfig]);*/

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
