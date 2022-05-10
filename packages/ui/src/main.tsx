import { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';

import Button from './components/essential/button';
import './styles/index.css';
import backend from './utils/backend';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(1);
    const [pyraIsSetUp, setPyraIsSetUp] = useState(false);
    const [checkingSetup, setCheckingSetup] = useState(true);

    async function updateCliStatus() {
        setCheckingSetup(true);
        const backendIsAvailable = await backend.isAvailable();
        const infoLogs = await backend.readInfoLogs();
        const debugLogs = await backend.readDebugLogs();
        const setupJSON = await backend.readSetupJSON();
        const parametersJSON = await backend.readParametersJSON();

        const updateSetupJSON = await backend.updateSetupJSON({
            opus: { em27_ip: '9.8.7.6' },
        });

        console.log({
            backendIsAvailable,
            infoLogs,
            debugLogs,
            setupJSON,
            parametersJSON,
            updateSetupJSON,
        });
        setPyraIsSetUp(backendIsAvailable);
        setCheckingSetup(false);
    }

    useEffect(() => {
        if (!pyraIsSetUp) {
            updateCliStatus();
        }
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
            {pyraIsSetUp && <p>pyra-4 command has been found</p>}
        </div>
    );
}

ReactDOM.render(<Main />, document.getElementById('root'));
