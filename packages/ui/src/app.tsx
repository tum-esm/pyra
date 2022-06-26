import { useCallback, useEffect, useState } from 'react';
import { ICONS } from './assets';
import { backend, reduxUtils } from './utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from './tabs';
import { essentialComponents, Header } from './components';
import toast, { resolveValue, Toaster } from 'react-hot-toast';
import { diff } from 'deep-diff';
import { customTypes } from './custom-types';
import { dialog } from '@tauri-apps/api';
import { Command } from '@tauri-apps/api/shell';
import { first } from 'lodash';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function App() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const [coreStateShouldBeLoaded, setCoreStateShouldBeLoaded] = useState(true);
    const [logsShouldBeLoaded, setLogsShouldBeLoaded] = useState(true);
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
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;
    const pyraCoreIsRunning = pyraCorePID !== undefined && pyraCorePID !== -1;
    const dispatch = reduxUtils.useTypedDispatch();

    useEffect(() => {
        loadInitialAppState().catch(console.error);
        startFileWatchers();
    }, []);

    useEffect(() => {
        const watchInterval = setInterval(startFileWatchers, 2000);
        return () => clearInterval(watchInterval);
    }, [fileWatcherChecksums]);

    useEffect(() => {
        if (logsShouldBeLoaded) {
            setLogsShouldBeLoaded(false);
            fetchLogsFile().catch(console.error);
        }
    }, [fetchLogsFile, logsShouldBeLoaded]);

    useEffect(() => {
        if (coreStateShouldBeLoaded) {
            setCoreStateShouldBeLoaded(false);
            fetchCoreState().catch(console.error);
        }
    }, [fetchCoreState, coreStateShouldBeLoaded]);

    useEffect(() => {
        if (configShouldBeLoaded) {
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

    async function fetchCoreState() {
        dispatch(reduxUtils.coreStateActions.setLoading(true));
        const result = await backend.getState();
        if (result.code !== 0) {
            console.error(`Could not fetch core state. processResult = ${JSON.stringify(result)}`);
            toast.error(`Could not fetch core state, please look in the console for details`);
        } else {
            const newCoreState = JSON.parse(result.stdout);
            dispatch(reduxUtils.coreStateActions.set(newCoreState));
        }
        dispatch(reduxUtils.coreStateActions.setLoading(false));
    }

    async function fetchConfig() {
        if (pyraCoreIsRunning) {
            const result = await backend.getConfig();
            if (result.code !== 0) {
                console.error(
                    `Could not fetch core state. processResult = ${JSON.stringify(result)}`
                );
                toast.error(`Could not fetch core state, please look in the console for details`);
                return;
            }

            const newCentralConfig: customTypes.config = JSON.parse(result.stdout);
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
    }

    const startFileWatchers = useCallback(async () => {
        let cmd = 'md5-windows';
        let filepaths = ['logs\\debug.log', 'runtime-data\\state.json', 'config\\config.json'];
        if (window.navigator.platform.includes('Mac')) {
            cmd = 'md5-mac';
            filepaths = filepaths.map((p) => p.replace('\\', '/'));
        }

        const result = await new Command(cmd, filepaths, {
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
            setLogsShouldBeLoaded(true);
            checksumsChanged = true;
            console.log('change in log files detected');
        }

        const newStateChecksum = getLine('state.json');
        if (newStateChecksum !== fileWatcherChecksums.state) {
            setCoreStateShouldBeLoaded(true);
            checksumsChanged = true;
            console.log('change in core state file detected');
        }

        const newConfigChecksum = getLine('config.json');
        if (newConfigChecksum !== fileWatcherChecksums.config) {
            setConfigShouldBeLoaded(true);
            checksumsChanged = true;
            console.log('change in config file detected');
        }

        if (checksumsChanged) {
            console.log({
                old: fileWatcherChecksums,
                new: {
                    logs: newLogsChecksum,
                    state: newStateChecksum,
                    config: newConfigChecksum,
                },
            });

            setFileWatcherChecksums({
                logs: newLogsChecksum,
                state: newStateChecksum,
                config: newConfigChecksum,
            });
        }
    }, [fileWatcherChecksums]);

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {backendIntegrity === undefined && (
                <main className="w-full h-full flex-row-center">
                    <div className="w-8 h-8 text-green-600 animate-spin">{ICONS.spinner}</div>
                </main>
            )}
            {(backendIntegrity === 'cli is missing' ||
                backendIntegrity === 'config is invalid') && (
                <main className="flex flex-col items-center justify-center w-full h-full bg-slate-100 gap-y-4">
                    <p className="inline max-w-sm text-center">
                        {backendIntegrity === 'cli is missing' && (
                            <>
                                <pre className="bg-slate-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
                                    pyra-cli
                                </pre>{' '}
                                has not been found on your system.{' '}
                            </>
                        )}
                        {backendIntegrity === 'config is invalid' && (
                            <>
                                The file{' '}
                                <pre className="bg-slate-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
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
                            'flex-grow w-full bg-slate-75 ' +
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
                    <Toaster
                        position="bottom-right"
                        toastOptions={{
                            duration: 24 * 3600 * 1000,
                        }}
                    >
                        {(t) => {
                            let typeIconColor = '';
                            let typeIcon = <></>;
                            switch (resolveValue(t.type, t)) {
                                case 'error':
                                    typeIconColor = 'text-red-400';
                                    typeIcon = ICONS.alert;
                                    break;
                                case 'success':
                                    typeIconColor = 'text-green-400';
                                    typeIcon = ICONS.check;
                                    break;
                            }
                            return (
                                <div
                                    className={'bg-white rounded-md shadow text-sm flex-row-center'}
                                    style={{ opacity: t.visible ? 1 : 0 }}
                                >
                                    <div
                                        className={`w-6 h-6 p-1 ml-1 mr-0.5 ${typeIconColor} flex-shrink-0`}
                                    >
                                        {typeIcon}
                                    </div>
                                    <div
                                        className={
                                            'pr-3 py-2 leading-tight text-sm text-slate-700 max-w-md'
                                        }
                                    >
                                        {resolveValue(t.message, t)}
                                    </div>
                                    <button
                                        onClick={() => toast.dismiss(resolveValue(t.id, t))}
                                        className={
                                            'h-full flex-row-center rounded-r-md cursor-pointer flex-shrink-0 ' +
                                            'bg-slate-100 hover:bg-slate-150 text-slate-600'
                                        }
                                    >
                                        <div className="w-6 h-6 mx-1">{ICONS.close}</div>
                                    </button>
                                </div>
                            );
                        }}
                    </Toaster>
                </>
            )}
        </div>
    );
}
