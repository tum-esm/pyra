import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { backend, reduxUtils } from './utils';
import { AutomationTab, ConfigTab, LogTab, ControlTab } from './tabs';
import { essentialComponents, Header } from './components';
import { watch } from 'tauri-plugin-fs-watch-api';

const tabs = ['Automation', 'Config', 'Logs', 'Enclosure Controls'];

export default function App() {
    const [activeTab, setActiveTab] = useState('Automation');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const dispatch = reduxUtils.useTypedDispatch();

    useEffect(() => {
        loadInitialState();
        fetchLogsFile();
        initializeLogsFileWatcher();
    }, []);

    async function loadInitialState() {
        setBackendIntegrity(undefined);
        console.debug('loading initial state ...');

        try {
            const pyraCliIsAvailable = await backend.pyraCliIsAvailable();
            console.debug('found pyra-cli');
            if (!pyraCliIsAvailable) {
                setBackendIntegrity('cli is missing');
                return;
            }

            const p = await backend.getConfig();
            if (p.stdout.startsWith('file not in a valid json format')) {
                setBackendIntegrity('config is invalid');
            } else {
                // TODO: handle "file not exists error"
                setBackendIntegrity('valid');
            }
        } catch (e) {
            console.log(`Error while fetching initial state: ${e}`);
            setBackendIntegrity('cli is missing');
        }
    }

    async function fetchLogsFile() {
        dispatch(reduxUtils.logsActions.setLoading(true));
        try {
            const newLogLines = (await backend.readDebugLogs()).stdout.split('\n');
            dispatch(reduxUtils.logsActions.set(newLogLines));
        } catch {
            // TODO: Add message to queue
        } finally {
            dispatch(reduxUtils.logsActions.setLoading(false));
        }
    }

    // TODO: watch for changes in config.json or state.json
    async function initializeLogsFileWatcher() {
        let logFilePath = import.meta.env.VITE_PROJECT_DIR + '\\logs\\debug.log';
        if (window.navigator.platform.includes('Mac')) {
            logFilePath = logFilePath.replace(/\\/g, '/');
        }
        await watch(logFilePath, { recursive: false }, (o) => {
            if (o.type === 'Write') {
                fetchLogsFile();
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
                    <essentialComponents.Button onClick={loadInitialState} variant="green">
                        retry connection
                    </essentialComponents.Button>
                </main>
            )}
            {backendIntegrity === 'valid' && (
                <>
                    <Header {...{ tabs, activeTab, setActiveTab }} />
                    <main className="flex-grow w-full min-h-0 bg-slate-75">
                        <AutomationTab visible={activeTab === 'Automation'} />
                        <ConfigTab visible={activeTab === 'Config'} />
                        <LogTab visible={activeTab === 'Logs'} />
                        <ControlTab visible={activeTab === 'Enclosure Controls'} />
                    </main>
                </>
            )}
        </div>
    );
}
