import * as React from 'react';
import * as ReactDOM from 'react-dom';

const tabs = [
    { label: 'First Tab', id: 'first' },
    { label: 'Second Tab', id: 'second' },
    { label: 'Third Tab', id: 'third' },
    { label: 'Fourth Tab', id: 'fourth' },
    { label: 'Fifth Tab', id: 'fifth' },
];

function Main() {
    const [activeTab, setActiveTab] = React.useState(tabs[0].id);

    return (
        <div className='flex flex-col items-stretch w-screen h-screen'>
            <header className='w-full flex-col px-6 pt-4'>
                <h1 className='text-2xl font-bold pb-2'>
                    Pyra{' '}
                    <span className='font-light bg-amber-200 text-amber-700 text-sm rounded px-1 py-0.5 ml-1'>
                        v4.0.0
                    </span>
                </h1>
                <div className='w-full flex flex-wrap py-2 gap-x-1 gap-y-1 border-b'>
                    {tabs.map(t => (
                        <button
                            className={
                                'px-3 py-0.5 rounded font-semibold cursor-pointer ' +
                                (t.id === activeTab
                                    ? 'bg-slate-300 text-black '
                                    : 'bg-white text-slate-500 hover:bg-slate-100 hover:text-slate-600')
                            }
                            onClick={() => setActiveTab(t.id)}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>
            </header>
            <main className='flex items-start justify-center flex-grow p-6'>
                <div className=' rounded shadow bg-gray-900 text-gray-100 px-2 py-1'>
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
