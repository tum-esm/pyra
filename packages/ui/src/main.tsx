import { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';

import backend from './utils/backend';
import Button from './components/essential/button';
import Header from './components/header';
import LogTab from './tabs/log-tab';
import StatusTab from './tabs/status-tab';
import TYPES from './utils/types';

const tabs = ['Status', 'Config', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTab, setActiveTab] = useState('Status');
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);
    const [centralConfig, setCentralConfig] = useState<TYPES.config | undefined>(
        undefined
    );

    useEffect(() => {
        loadInitialState();
    }, []);

    async function loadInitialState() {
        setBackendIntegrity(undefined);
        setCentralConfig(undefined);

        const pyraCliIsAvailable = await backend.pyraCliIsAvailable();
        if (!pyraCliIsAvailable) {
            setBackendIntegrity('cli is missing');
            return;
        }

        const p = await backend.getConfig();
        if (p.stdout.startsWith('file not in a valid json format')) {
            setBackendIntegrity('config is invalid');
        } else {
            setBackendIntegrity('valid');
            setCentralConfig(JSON.parse(p.stdout));
        }
    }

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {(backendIntegrity === 'cli is missing' ||
                backendIntegrity === 'config is invalid') && (
                <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
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
                    <Button onClick={loadInitialState} variant="green">
                        retry connection
                    </Button>
                </main>
            )}
            {backendIntegrity === 'valid' && centralConfig !== undefined && (
                <>
                    <Header {...{ tabs, activeTab, setActiveTab }} />
                    <main className="flex-grow w-full min-h-0 bg-gray-100">
                        <StatusTab
                            visible={activeTab === 'Status'}
                            {...{ centralConfig, setCentralConfig }}
                        />
                        <LogTab visible={activeTab === 'Logs'} />
                    </main>
                </>
            )}
        </div>
    );
}

ReactDOM.render(<Main />, document.getElementById('root'));
