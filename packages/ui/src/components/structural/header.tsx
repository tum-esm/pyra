import { ask } from '@tauri-apps/api/dialog';
import { reduxUtils } from '../../utils';

export default function Header(props: {
    tabs: string[];
    activeTab: string;
    setActiveTab(t: string): void;
}) {
    const { tabs, activeTab, setActiveTab } = props;
    const plcIsControlledByUser = reduxUtils.useTypedSelector(
        (s) => s.config.central?.tum_plc?.controlled_by_user
    );

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
        <header className="z-50 flex flex-row items-center flex-shrink-0 w-full px-2 py-0 bg-gray-900 shadow h-14">
            <h1 className="pl-3 text-2xl font-semibold text-center text-white whitespace-nowrap">
                PYRA <span className="pl-0.5 text-lg font-normal opacity-50">{APP_VERSION}</span>
            </h1>
            <div className="flex-grow " />
            <div className="flex flex-wrap justify-center px-4 py-2 gap-x-2 gap-y-2">
                {tabs.map((t, i) => (
                    <button
                        key={i}
                        className={
                            'px-4 py-1.5 rounded font-medium cursor-pointer text-base ' +
                            (t === activeTab
                                ? 'bg-gray-600 text-white '
                                : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200')
                        }
                        onClick={() => monitoredSetActiveTab(t)}
                    >
                        {t}
                    </button>
                ))}
            </div>
        </header>
    );
}
