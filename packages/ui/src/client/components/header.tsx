import React from 'react';

export default function Header(props: {
    tabs: string[];
    activeTabIndex: number;
    setActiveTabIndex(i: number): void;
}) {
    return (
        <header className='flex flex-row items-center w-full px-2 py-2 bg-slate-900'>
            <h1 className='pl-3 text-2xl font-bold text-center text-white whitespace-nowrap'>
                PyRa{' '}
                <span className='pl-0.5 font-normal opacity-50'>4.0.0</span>
            </h1>
            <div className='flex-grow ' />
            <div className='flex flex-wrap justify-center px-4 py-3 gap-x-2 gap-y-2'>
                {props.tabs.map((t, i) => (
                    <button
                        className={
                            'px-3 py-0.5 rounded font-medium cursor-pointer ' +
                            (i === props.activeTabIndex
                                ? 'bg-slate-600 text-white '
                                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200')
                        }
                        onClick={() => props.setActiveTabIndex(i)}
                    >
                        {t}
                    </button>
                ))}
            </div>
        </header>
    );
}
