import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import Header from './components/header';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = useState(0);

    return (
        <div className='flex flex-col items-stretch w-screen h-screen'>
            <Header {...{ tabs, activeTabIndex, setActiveTabIndex }} />
            <main className='flex items-start justify-center flex-grow p-6'>
                <div className='px-2 py-1 text-gray-100 bg-gray-900 rounded shadow '>
                    React + Tailwind + Typescript + Electron = ❤
                </div>
            </main>
        </div>
    );
}

function render() {
    ReactDOM.render(<Main />, document.body);
}

render();
