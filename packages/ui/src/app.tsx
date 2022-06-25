import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { backend, reduxUtils } from './utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from './tabs';
import { essentialComponents, Header } from './components';
import { watch } from 'tauri-plugin-fs-watch-api';
import toast, { resolveValue, Toaster } from 'react-hot-toast';
import { customTypes } from './custom-types';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function App() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const centralConfigTumPlc = reduxUtils.useTypedSelector((s) => s.config.central?.tum_plc);
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
    const enclosureControlsIsVisible =
        centralConfigTumPlc !== null && centralConfigTumPlc !== undefined;

    const pyraCoreIsRunning = pyraCorePID !== undefined && pyraCorePID !== -1;

    const dispatch = reduxUtils.useTypedDispatch();
    const setConfigs = (c: customTypes.config | undefined) =>
        dispatch(reduxUtils.configActions.setConfigs(c));

    useEffect(() => {
        loadInitialAppState();
        fetchLogsFile();
        fetchCoreState();
        initializeFileWatchers();
    }, []);

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
                setConfigs(newConfig);
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
        if (pyraCoreIsRunning) {
            dispatch(reduxUtils.coreStateActions.setLoading(true));
            const result = await backend.getState();
            try {
                const newCoreState = JSON.parse(result.stdout);
                dispatch(reduxUtils.coreStateActions.set(newCoreState));
            } catch {
                console.error(
                    `Could not fetch core state. processResult = ${JSON.stringify(result)}`
                );
                toast.error(`Could not fetch core state, please look in the console for details`);
            } finally {
                dispatch(reduxUtils.coreStateActions.setLoading(false));
            }
        }
    }

    // TODO: watch for changes in config.json
    async function initializeFileWatchers() {
        let logFilePath = import.meta.env.VITE_PROJECT_DIR + '\\logs\\debug.log';
        let stateFilePath = import.meta.env.VITE_PROJECT_DIR + '\\runtime-data\\state.json';

        if (window.navigator.platform.includes('Mac')) {
            logFilePath = logFilePath.replace(/\\/g, '/');
            stateFilePath = stateFilePath.replace(/\\/g, '/');
        }

        await watch(logFilePath, { recursive: false }, (o) => {
            if (o.type === 'Write') {
                fetchLogsFile();
            }
        });
        await watch(stateFilePath, { recursive: false }, (o) => {
            if (o.type === 'Write') {
                fetchCoreState();
            }
        });
    }

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
