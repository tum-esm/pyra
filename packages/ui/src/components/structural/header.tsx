export default function Header(props: {
    tabs: string[];
    activeTab: string;
    setActiveTab(s: string): void;
}) {
    return (
        <header className="z-50 flex flex-row items-center flex-shrink-0 w-full px-2 py-0 bg-gray-900 shadow h-14">
            <h1 className="pl-3 text-2xl font-bold text-center text-white whitespace-nowrap">
                PyRa <span className="pl-0.5 font-normal opacity-50">{APP_VERSION}</span>
            </h1>
            <div className="flex-grow " />
            <div className="flex flex-wrap justify-center px-4 py-2 gap-x-2 gap-y-2">
                {props.tabs.map((t, i) => (
                    <button
                        key={i}
                        className={
                            'px-3 py-1 rounded font-medium cursor-pointer text-base ' +
                            (t === props.activeTab
                                ? 'bg-gray-600 text-white '
                                : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200')
                        }
                        onClick={() => props.setActiveTab(t)}
                    >
                        {t}
                    </button>
                ))}
            </div>
        </header>
    );
}
