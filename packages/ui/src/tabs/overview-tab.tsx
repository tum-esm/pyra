import { reduxUtils } from '../utils';

export default function OverviewTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.body);

    // TODO: Implement core state
    // TODO: Implement measurement state
    // TODO: Implement plc readings + close cover
    // TODO: Implement system stats
    // TODO: Implement last iterations logs

    return (
        <div className={'flex-col-center w-full h-full overflow-y-scroll gap-y-4 py-4 px-6'}>
            <div>pyra core state </div>
            <div>measurement state </div>
            <div className="w-full h-px bg-gray-300" />
            <div>plc readings, force close cover button </div>
            <div>system stats: {JSON.stringify(coreState)}</div>
            <div className="w-full h-px bg-gray-300" />
            <div>last iterations info logs</div>
        </div>
    );
}
