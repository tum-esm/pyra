import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import TabLogs from './components/tab-logs';
import Header from './components/header';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(3);

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
                    <TabLogs />
                </div>
            </main>
        </div>
    );
}

function render() {
    ReactDOM.render(<Main />, document.body);
}

render();
