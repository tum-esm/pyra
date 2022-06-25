import { automationComponents } from '../components';
import { reduxUtils } from '../utils';

export default function AutomationTab() {
    const coreProcessPID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    return (
        <div className={'flex flex-col w-full h-full overflow-y-scroll gap-y-4 py-4'}>
            <automationComponents.PyraCoreStatus />
            <div className="w-full h-px bg-slate-300" />
            {coreProcessPID !== undefined && coreProcessPID !== -1 && (
                <automationComponents.MeasurementDecisionStatus />
            )}
        </div>
    );
}
