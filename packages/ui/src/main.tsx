import { useEffect, useState } from 'react';
import { Command } from '@tauri-apps/api/shell';
import ReactDOM from 'react-dom';
import './styles/index.css';

import Button from './components/essential/button';
import Header from './components/header';
import LogTab from './tabs/log-tab';
import backend from './utils/backend';

const tabs = ['Status', 'Config', 'Logs', 'Enclosure Controls'];

async function runCommand() {
    const command = new Command('pyra-cli-core-is-running', [], {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    });
    const p = await command.execute();
    console.log({ p });
}

function Main() {
    console.log('RUNNING MAINS');
    const [activeTabIndex, setActiveTabIndex] = useState(1);
    const [pyraIsSetUp, setPyraIsSetUp] = useState(false);
    const [checkingSetup, setCheckingSetup] = useState(true);

    async function updateCliStatus() {
        setCheckingSetup(true);
        const status = await backend.isAvailable();
        setPyraIsSetUp(status);
        setCheckingSetup(false);
    }

    useEffect(() => {
        if (!pyraIsSetUp) {
            updateCliStatus();
        }
        runCommand();
    }, []);

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {!pyraIsSetUp && !checkingSetup && (
                <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
                    <p className="max-w-sm text-center">
                        <pre className="bg-slate-200 mr-1 px-1 py-0.5 rounded-sm font-bold inline">
                            pyra-cli
                        </pre>{' '}
                        has not been found on your system. Please following the
                        installation instructions on{' '}
                        <span className="font-bold text-blue-500 underline">
                            https://github.com/tum-esm/pyra
                        </span>
                        .
                    </p>
                    <Button onClick={updateCliStatus} variant="green">
                        retry connection
                    </Button>
                </main>
            )}
            {pyraIsSetUp && (
                <>
                    <Header {...{ tabs, activeTabIndex, setActiveTabIndex }} />
                    <main className="flex-grow w-full min-h-0 bg-gray-100">
                        <LogTab visible={tabs[activeTabIndex] === 'Logs'} />
                    </main>
                </>
            )}
        </div>
    );
}

ReactDOM.render(<Main />, document.getElementById('root'));
