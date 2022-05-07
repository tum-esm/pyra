import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import ConfigTab from './tabs/config-tab';
import LogTab from './tabs/log-tab';
import Header from './components/header';
import Button from './components/essential/button';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(1);
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
                <main className='flex flex-col items-center justify-center w-full h-full gap-y-4 bg-slate-300'>
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
                    <Button onClick={updateCliStatus} variant='green'>
                        retry connection
                    </Button>
                </main>
            )}
            {pyraIsSetUp && (
                <>
                    <Header {...{ tabs, activeTabIndex, setActiveTabIndex }} />
                    <main className='flex-grow w-full min-h-0 bg-slate-200'>
                        <ConfigTab
                            type='setup'
                            visible={tabs[activeTabIndex] === 'Setup'}
                        />
                        <ConfigTab
                            type='parameters'
                            visible={tabs[activeTabIndex] === 'Parameters'}
                        />
                        <LogTab visible={tabs[activeTabIndex] === 'Logs'} />
                    </main>
                </>
            )}
        </div>
    );
}

ReactDOM.render(<Main />, document.getElementById('react-root-node'));
