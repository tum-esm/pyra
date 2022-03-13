import * as React from 'react';
import * as ReactDOM from 'react-dom';

const tabs = ['Status', 'Setup', 'Parameters', 'Logs', 'Enclosure Controls'];

function Main() {
    const [activeTabIndex, setActiveTabIndex] = React.useState(0);

    return (
        <div className='flex flex-col items-stretch w-screen h-screen'>
            <header className='flex-col w-full pt-4 bg-slate-900'>
                <h1 className='pb-1 text-3xl font-bold text-center text-white'>
                    PyRa{' '}
                    <span className='font-normal bg-amber-200 text-amber-700 text-sm rounded px-1 py-[0.0625rem] ml-1.5'>
                        v4.0.0
                    </span>
                </h1>
                <div className='flex flex-wrap justify-center w-full px-4 py-3 gap-x-2 gap-y-2'>
                    {tabs.map((t, i) => (
                        <button
                            className={
                                'px-3 py-0.5 rounded font-medium cursor-pointer ' +
                                (i === activeTabIndex
                                    ? 'bg-slate-600 text-white '
                                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200')
                            }
                            onClick={() => setActiveTabIndex(i)}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </header>
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
