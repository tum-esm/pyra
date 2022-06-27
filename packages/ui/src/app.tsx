import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { fetchUtils, reduxUtils } from './utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from './tabs';
import { structuralComponents } from './components';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function App() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const [logsShouldBeLoaded, setLogsShouldBeLoaded] = useState(true);
    const [coreStateShouldBeLoaded, setCoreStateShouldBeLoaded] = useState(false);
    const [configShouldBeLoaded, setConfigShouldBeLoaded] = useState(false);

    const [fileWatcherChecksums, setFileWatcherChecksums] = useState({
        logs: '',
        coreState: '',
        config: '',
    });

    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.content);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;
    const pyraCoreIsRunning = pyraCorePID !== undefined && pyraCorePID !== -1;
    const dispatch = reduxUtils.useTypedDispatch();

    useEffect(() => {
        fetchUtils.initialAppState(dispatch, setBackendIntegrity).catch(console.error);
    }, [dispatch, setBackendIntegrity]);

    console.log({ backendIntegrity });

    useEffect(() => {
        const watchInterval = setInterval(
            () =>
                fetchUtils.detectFileChanges(
                    fileWatcherChecksums,
                    setLogsShouldBeLoaded,
                    setCoreStateShouldBeLoaded,
                    setConfigShouldBeLoaded,
                    setFileWatcherChecksums
                ),
            2000
        );
        return () => clearInterval(watchInterval);
    }, [dispatch, fileWatcherChecksums]);

    useEffect(() => {
        if (logsShouldBeLoaded) {
            console.log('loading logs');
            setLogsShouldBeLoaded(false);
            fetchUtils.logs(dispatch).catch(console.error);
        }
    }, [dispatch, logsShouldBeLoaded]);

    useEffect(() => {
        if (
            coreStateShouldBeLoaded &&
            centralConfig !== undefined &&
            pyraCoreIsRunning !== undefined
        ) {
            console.log('loading core state');
            setCoreStateShouldBeLoaded(false);
            fetchUtils.coreState(dispatch, centralConfig, pyraCoreIsRunning).catch(console.error);
        }
    }, [dispatch, coreStateShouldBeLoaded, centralConfig, pyraCoreIsRunning]);

    useEffect(() => {
        if (configShouldBeLoaded && centralConfig !== undefined) {
            console.log('loading config');
            setConfigShouldBeLoaded(false);
            fetchUtils.config(dispatch, centralConfig).catch(console.error);
        }
    }, [dispatch, configShouldBeLoaded, centralConfig]);

    // Fetch PLC State via CLI when PLC is controlled by user
    useEffect(() => {
        if (centralConfig !== undefined && pyraCorePID !== undefined) {
            // load stuff directly from PLC if pyraCore is not running
            // or user has set the PLC interaction to manual
            if (!pyraCoreIsRunning || centralConfig.tum_plc?.controlled_by_user === true) {
                const watchInterval = setInterval(() => setCoreStateShouldBeLoaded(true), 5000);
                return () => clearInterval(watchInterval);
            }
        }
    }, [coreState, pyraCorePID, centralConfig]);

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {backendIntegrity === undefined && (
                <main className="w-full h-full flex-row-center">
                    <div className="w-8 h-8 text-green-600 animate-spin">{ICONS.spinner}</div>
                </main>
            )}
            {(backendIntegrity === 'cli is missing' ||
                backendIntegrity === 'config is invalid') && (
                <structuralComponents.DisconnectedScreen
                    backendIntegrity={backendIntegrity}
                    loadInitialAppState={() =>
                        fetchUtils.initialAppState(dispatch, setBackendIntegrity)
                    }
                />
            )}
            {backendIntegrity === 'valid' && (
                <>
                    <structuralComponents.Header
                        {...{
                            tabs: [
                                ...tabs,
                                ...(enclosureControlsIsVisible ? ['PLC Controls'] : []),
                            ],
                            activeTab,
                            setActiveTab,
                        }}
                    />
                    <main
                        className={
                            'flex-grow w-full bg-gray-75 ' +
                            'h-[calc(200vh-1.5rem)] overflow-y-scroll'
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
                </>
            )}
        </div>
    );
}
