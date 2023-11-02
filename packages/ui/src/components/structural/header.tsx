import { ask } from '@tauri-apps/api/dialog';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';
import { IconBugFilled, IconBook } from '@tabler/icons-react';

export function Header(props: {
    tabs: string[];
    activeTab: string;
    setActiveTab(t: string): void;
}) {
    const { tabs, activeTab, setActiveTab } = props;
    const { centralConfig } = useConfigStore();
    const plcIsControlledByUser = centralConfig?.tum_plc?.controlled_by_user;

    async function monitoredSetActiveTab(t: string) {
        if (
            activeTab === 'PLC Controls' &&
            t !== 'PLC Controls' &&
            plcIsControlledByUser === true
        ) {
            const switchTabsAnyways = await ask('Switch tabs anyways?', {
                title: 'PLC is still controlled by user',
                type: 'warning',
            });
            if (switchTabsAnyways) {
                setActiveTab(t);
            }
        } else {
            setActiveTab(t);
        }
    }

    return (
        <header className="z-50 flex flex-row items-center flex-shrink-0 w-full px-2 py-0 bg-white border-b h-14 border-slate-300">
            <h1 className="pl-3 text-2xl font-semibold text-center text-slate-800 whitespace-nowrap">
                PYRA <span className="pl-0.5 text-lg font-normal opacity-60">{APP_VERSION}</span>
            </h1>
            <div className="flex-grow " />
            <div className="flex flex-wrap justify-center h-full gap-x-2 gap-y-2">
                {tabs.map((t, i) => (
                    <div
                        key={t}
                        className={
                            'h-full py-2 border-b-[3px] ' +
                            (t === activeTab ? 'border-slate-900 ' : 'border-transparent')
                        }
                    >
                        <button
                            key={i}
                            className={
                                'px-4 py-1.5 rounded-md font-medium cursor-pointer text-base h-full ' +
                                (t === activeTab
                                    ? 'text-slate-950 '
                                    : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800')
                            }
                            onClick={() => monitoredSetActiveTab(t)}
                        >
                            {t}
                        </button>
                    </div>
                ))}
            </div>
            <div className="w-px h-full mx-4 bg-slate-300" />
            <a
                className="w-10 h-10 p-2.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-950 mr-2"
                title="Documentation"
                href="https://pyra.esm.ei.tum.de/docs"
                target="_blank"
            >
                <IconBook className="w-5 h-5" />
            </a>
            <a
                className="w-10 h-10 p-2.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-950 mr-2"
                title="Issue Tracker"
                href="https://github.com/tum-esm/pyra/issues"
                target="_blank"
            >
                <IconBugFilled className="w-5 h-5" />
            </a>
        </header>
    );
}

export function BlankHeader() {
    return (
        <header className="z-50 flex flex-row items-center flex-shrink-0 w-full px-2 py-0 bg-white border-b h-14 border-slate-300">
            <h1 className="pl-3 text-2xl font-semibold text-center text-slate-800 whitespace-nowrap">
                PYRA <span className="pl-0.5 text-lg font-normal opacity-60">{APP_VERSION}</span>
            </h1>
            <div className="flex-grow " />
        </header>
    );
}
