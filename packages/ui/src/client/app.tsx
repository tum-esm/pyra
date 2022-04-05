import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import LogTab from './tabs/log-tab';
import Header from './components/header';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(0);

    // TODO: Check for pyra-cli state on startup
    // TODO: Render placeholder tab with instructions
    // TODO: Add button to refresh pyra-cli state

    return (
        <div className='flex flex-col items-stretch w-screen h-screen overflow-hidden'>
            <Header {...{ tabs, activeTabIndex, setActiveTabIndex }} />
            <main className='flex-grow w-full min-h-0 bg-slate-200'>
                <div
                    className={
                        'w-full h-full ' +
                        (tabs[activeTabIndex] === 'Logs' ? 'block ' : 'hidden')
                    }
                >
                    <LogTab />
                </div>
            </main>
        </div>
    );
}

function render() {
    ReactDOM.render(<Main />, document.body);
}

render();
