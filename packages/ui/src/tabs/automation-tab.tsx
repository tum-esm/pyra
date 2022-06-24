import { useState } from 'react';
import { automationComponents } from '../components';

export default function AutomationTab() {
    // "undefined" indicates that the pyra-core state is currently
    // being checked, "-1" indicates that pyra-core is not running
    const [pyraCorePID, setPyraCorePID] = useState<number | undefined>(undefined);

    return (
        <div className={'flex flex-col w-full h-full overflow-y-scroll gap-y-4 py-4'}>
            <automationComponents.PyraCoreStatus {...{ pyraCorePID, setPyraCorePID }} />
            <div className="w-full h-px bg-slate-300" />
            {pyraCorePID !== undefined && pyraCorePID !== -1 && (
                <>
                    <automationComponents.MeasurementDecisionStatus />
                </>
            )}
        </div>
    );
}
