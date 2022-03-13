import React from 'react';

export default function Header(props: {
    tabs: string[];
    activeTabIndex: number;
    setActiveTabIndex(i: number): void;
}) {
    return (
        <header className='flex-col w-full pt-4 bg-slate-900'>
            <h1 className='pb-1 text-3xl font-bold text-center text-white'>
                PyRa{' '}
                <span className='font-normal bg-amber-200 text-amber-700 text-sm rounded px-1 py-[0.0625rem] ml-1.5'>
                    v4.0.0
                </span>
            </h1>
            <div className='flex flex-wrap justify-center w-full px-4 py-3 gap-x-2 gap-y-2'>
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
