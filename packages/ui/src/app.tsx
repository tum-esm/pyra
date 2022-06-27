import { useCallback, useEffect, useState } from 'react';
import { ICONS } from './assets';
import { backend, reduxUtils } from './utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from './tabs';
import { essentialComponents, Header } from './components';
import toast from 'react-hot-toast';
import { diff } from 'deep-diff';
import { customTypes } from './custom-types';
import { dialog, shell } from '@tauri-apps/api';
import { first } from 'lodash';
import MessageQueue from './components/message-queue';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function App() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const [logsShouldBeLoaded, setLogsShouldBeLoaded] = useState(true);
    const [coreStateShouldBeLoaded, setCoreStateShouldBeLoaded] = useState(false);
    const [configShouldBeLoaded, setConfigShouldBeLoaded] = useState(false);

    const [fileWatcherChecksums, setFileWatcherChecksums] = useState<{
        logs: string | undefined;
        state: string | undefined;
        config: string | undefined;
    }>({
        logs: '',
        state: '',
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
        loadInitialAppState().catch(console.error);
    }, []);

    useEffect(() => {
        const watchInterval = setInterval(detectFileChanges, 2000);
        return () => clearInterval(watchInterval);
    }, [fileWatcherChecksums]);

    useEffect(() => {
        if (logsShouldBeLoaded) {
            console.log('loading logs');
            setLogsShouldBeLoaded(false);
            fetchLogsFile().catch(console.error);
        }
    }, [fetchLogsFile, logsShouldBeLoaded]);

    useEffect(() => {
        if (coreStateShouldBeLoaded) {
            console.log('loading core state');
            setCoreStateShouldBeLoaded(false);
            fetchCoreState().catch(console.error);
        }
    }, [coreStateShouldBeLoaded]);

    useEffect(() => {
        if (configShouldBeLoaded) {
            console.log('loading config');
            setConfigShouldBeLoaded(false);
            fetchConfig().catch(console.error);
        }
    }, [fetchConfig, configShouldBeLoaded, centralConfig]);

    /*
    1. Check whether pyra-cli is available
    2. Check whether config can be read
    3. Possibly add config to reduxStore
    */
    async function loadInitialAppState() {
        setBackendIntegrity(undefined);
        console.debug('loading initial state ...');

        const result = await backend.pyraCliIsAvailable();
        if (result.stdout.includes('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...')) {
            console.debug('found pyra-cli');
        } else {
            console.error(`Could not reach pyra-cli. processResult = ${JSON.stringify(result)}`);
            setBackendIntegrity('cli is missing');
            return;
        }

        const result2 = await backend.getConfig();
        if (result2.stdout.startsWith('file not in a valid json format')) {
            setBackendIntegrity('config is invalid');
        } else {
            try {
                const newConfig = JSON.parse(result2.stdout);
                dispatch(reduxUtils.configActions.setConfigs(newConfig));
                setBackendIntegrity('valid');
            } catch (e) {
                console.error(
                    `Could not fetch config file. processResult = ${JSON.stringify(result2)}`
                );
                setBackendIntegrity('config is invalid');
            }
        }
    }

    async function fetchLogsFile() {
        dispatch(reduxUtils.logsActions.setLoading(true));
        const result = await backend.readDebugLogs();
        if (result.code === 0) {
            const newLogLines = result.stdout.split('\n');
            dispatch(reduxUtils.logsActions.set(newLogLines));
        } else {
            console.error(`Could not fetch log files. processResult = ${JSON.stringify(result)}`);
            toast.error('Could not fetch log files - details in the console');
        }
        dispatch(reduxUtils.logsActions.setLoading(false));
    }

    const fetchCoreState = useCallback(async () => {
        dispatch(reduxUtils.coreStateActions.setLoading(true));
        let result: shell.ChildProcess;
        if (pyraCoreIsRunning && centralConfig?.tum_plc?.controlled_by_user === false) {
            result = await backend.getState();
        } else {
            result = await backend.readFromPLC();
        }

        if (result.code !== 0) {
            console.error(`Could not fetch core state. processResult = ${JSON.stringify(result)}`);
            toast.error(`Could not fetch core state, please look in the console for details`);
        } else {
            try {
                const newCoreState = JSON.parse(result.stdout);
                dispatch(reduxUtils.coreStateActions.set(newCoreState));
            } catch {
                toast.error(`Could not fetch core state: ${result.stdout}`);
            }
        }
        dispatch(reduxUtils.coreStateActions.setLoading(false));
    }, [pyraCoreIsRunning, centralConfig]);

    async function fetchConfig() {
        const result = await backend.getConfig();
        if (result.code !== 0) {
            console.error(`Could not fetch core state. processResult = ${JSON.stringify(result)}`);
            toast.error(`Could not fetch core state, please look in the console for details`);
            return;
        }

        const newCentralConfig: customTypes.config = JSON.parse(result.stdout);
        const diffsToCentral = diff(centralConfig, newCentralConfig);
        console.log({ centralConfig, newCentralConfig, diffsToCentral });
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

    const detectFileChanges = useCallback(async () => {
        let cmd = 'md5-windows';
        let filepaths = ['logs\\debug.log', 'runtime-data\\state.json', 'config\\config.json'];
        if (window.navigator.platform.includes('Mac')) {
            cmd = 'md5-mac';
            filepaths = filepaths.map((p) => p.replace('\\', '/'));
        }

        const result = await new shell.Command(cmd, filepaths, {
            cwd: import.meta.env.VITE_PROJECT_DIR,
        }).execute();

        if (result.code !== 0) {
            toast.error('File watcher is not working - details in console');
            console.error(`File watcher is not working, processResult = ${JSON.stringify(result)}`);
            return;
        }

        const getLine = (indicator: string) =>
            first(result.stdout.split('\n').filter((line) => line.includes(indicator)));

        let checksumsChanged = false;

        const newLogsChecksum = getLine('debug.log');
        if (newLogsChecksum !== fileWatcherChecksums.logs) {
            if (fileWatcherChecksums.logs !== '') {
                setLogsShouldBeLoaded(true);
                console.log('change in log files detected');
            }
            checksumsChanged = true;
        }

        const newStateChecksum = getLine('state.json');
        if (newStateChecksum !== fileWatcherChecksums.state) {
            if (fileWatcherChecksums.state !== '') {
                setCoreStateShouldBeLoaded(true);
                console.log('change in core state file detected');
            }
            checksumsChanged = true;
        }

        const newConfigChecksum = getLine('config.json');
        if (newConfigChecksum !== fileWatcherChecksums.config) {
            if (fileWatcherChecksums.config !== '') {
                // wait 2 second to make sure all state changes have propagated
                setTimeout(() => setConfigShouldBeLoaded(true), 2000);
                console.log('change in config file detected');
            }
            checksumsChanged = true;
        }

        if (checksumsChanged) {
            setFileWatcherChecksums({
                logs: newLogsChecksum,
                state: newStateChecksum,
                config: newConfigChecksum,
            });
        }
    }, [fileWatcherChecksums]);

    // Fetch PLC State via CLI when PLC is controlled by user
    useEffect(() => {
        if (centralConfig !== undefined && pyraCorePID !== undefined) {
            if (centralConfig.tum_plc !== null) {
                if (coreState === undefined) {
                    setCoreStateShouldBeLoaded(true);
                }

                // load stuff directly from PLC if pyraCore is not running
                // or user has set the PLC interaction to manual
                if (!pyraCoreIsRunning || centralConfig.tum_plc.controlled_by_user === true) {
                    const watchInterval = setInterval(() => setCoreStateShouldBeLoaded(true), 5000);
                    return () => clearInterval(watchInterval);
                }
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
                <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
                    <p className="inline max-w-sm text-center">
                        {backendIntegrity === 'cli is missing' && (
                            <>
                                <pre className="bg-gray-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
                                    pyra-cli
                                </pre>{' '}
                                has not been found on your system.{' '}
                            </>
                        )}
                        {backendIntegrity === 'config is invalid' && (
                            <>
                                The file{' '}
                                <pre className="bg-gray-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
                                    config.json
                                </pre>{' '}
                                is not in a valid JSON format.{' '}
                            </>
                        )}
                        Please following the installation instructions on{' '}
                        <span className="font-bold text-blue-500 underline">
                            https://github.com/tum-esm/pyra
                        </span>
                        .
                    </p>
                    <essentialComponents.Button onClick={loadInitialAppState} variant="green">
                        retry connection
                    </essentialComponents.Button>
                </main>
            )}
            {backendIntegrity === 'valid' && (
                <>
                    <Header
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
                    <MessageQueue />
                </>
            )}
        </div>
    );
}
