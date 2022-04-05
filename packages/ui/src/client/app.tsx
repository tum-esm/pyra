import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import LogTab from './tabs/log-tab';
import Header from './components/header';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(0);
    const [pyraIsSetUp, setPyraIsSetUp] = useState(false);
    const [checkingSetup, setCheckingSetup] = useState(true);

    async function updateCliStatus() {
        setCheckingSetup(true);
        const status = await window.electron.checkCLIStatus();
        setPyraIsSetUp(status);
        setCheckingSetup(false);
    }

    useEffect(() => {
        if (!pyraIsSetUp) {
            updateCliStatus();
        }
    }, []);

    return (
        <div className='flex flex-col items-stretch w-screen h-screen overflow-hidden'>
            {!pyraIsSetUp && !checkingSetup && (
                <main className='flex flex-col items-center justify-center w-full h-full gap-y-4'>
                    <p className='max-w-sm text-center'>
                        <pre className='bg-slate-200 mr-1 px-1 py-0.5 rounded-sm font-bold inline'>
                            pyra-cli
                        </pre>{' '}
                        has not been found on your system. Please following the
                        installation instructions on{' '}
                        <span className='font-bold text-blue-500 underline'>
                            https://github.com/tum-esm/pyra
                        </span>
                        .
                    </p>
                    <button
                        onClick={updateCliStatus}
                        className='px-2 py-0.5 text-green-800 bg-green-200 rounded font-medium hover:bg-green-300 hover:text-green-900'
                    >
                        Retry connection
                    </button>
                </main>
            )}
            {pyraIsSetUp && (
                <>
                    <Header {...{ tabs, activeTabIndex, setActiveTabIndex }} />
                    <main className='flex-grow w-full min-h-0 bg-slate-200'>
                        <div
                            className={
                                'w-full h-full ' +
                                (tabs[activeTabIndex] === 'Logs'
                                    ? 'block '
                                    : 'hidden')
                            }
                        >
                            <LogTab />
                        </div>
                    </main>
                </>
            )}
        </div>
    );
}

function render() {
    ReactDOM.render(<Main />, document.body);
}

render();
