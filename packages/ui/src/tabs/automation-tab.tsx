import { automationComponents } from '../components';
import { reduxUtils } from '../utils';

export default function AutomationTab() {
    const coreProcessPID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    const pyraIsInTestMode = reduxUtils.useTypedSelector(
        (s) => s.config.central?.general.test_mode
    );

    return (
        <div className={'flex flex-col w-full gap-y-4 py-4'}>
            <automationComponents.PyraCoreStatus />
            <div className="w-full h-px bg-gray-300" />
            {pyraIsInTestMode && (
                <div className="w-full text-sm flex-row-center">
                    No measurement decision when pyra is in test mode
                </div>
            )}
            {!pyraIsInTestMode && coreProcessPID !== undefined && coreProcessPID !== -1 && (
                <automationComponents.MeasurementDecisionStatus />
            )}
        </div>
    );
}
