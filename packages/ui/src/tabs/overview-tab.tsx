export default function OverviewTab() {
    return (
        <div className={'flex-col-center w-full h-full overflow-y-scroll gap-y-4 py-4 px-6'}>
            <div>pyra core state </div>
            <div>measurement state </div>
            <div className="w-full h-px bg-gray-300" />
            <div>plc readings, force close cover button </div>
            <div>system stats</div>
            <div className="w-full h-px bg-gray-300" />
            <div>last iterations info logs</div>
        </div>
    );
}
