import { reduxUtils } from '../utils';
import { essentialComponents } from '../components';

export default function OverviewTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.body);
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    // TODO: Implement core state
    // TODO: Implement measurement state
    // TODO: Implement plc readings + close cover
    // TODO: Implement system stats

    const allInfoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
    const currentInfoLogLines =
        allInfoLogLines === undefined ? ['...'] : allInfoLogLines.slice(-10);

    return (
        <div className={'flex-col-center w-full h-full overflow-y-scroll gap-y-4 pt-4 pb-12 px-6'}>
            <div className="w-full text-sm h-7 flex-row-left">
                <essentialComponents.Ping state={true} />
                <span className="ml-2.5 mr-1">
                    pyra-core is running with process ID {pyraCorePID}
                </span>
            </div>
            <div>measurement state </div>
            <div className="w-full h-px bg-gray-300" />
            <div>plc readings, force close cover button </div>
            <div>system stats: {JSON.stringify(coreState)}</div>
            <div className="w-full h-px bg-gray-300" />
            <div className="w-full font-medium">Last 10 log lines:</div>
            <pre
                className={
                    'w-full py-2 !mb-0 overflow-x-auto bg-white flex-grow ' +
                    'border border-gray-250 shadow-sm rounded-md -mt-2'
                }
            >
                <code className="w-full h-full !text-xs">
                    {currentInfoLogLines.map((l, i) => (
                        <essentialComponents.LogLine key={`${i} ${l}`} text={l} />
                    ))}
                </code>
            </pre>
        </div>
    );
}
