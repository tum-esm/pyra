import { useState } from 'react';
import { automationComponents } from '../components';

export default function AutomationTab(props: { visible: boolean }) {
    // "undefined" indicates that the pyra-core state is currently
    // being checked, "-1" indicates that pyra-core is not running
    const [pyraCorePID, setPyraCorePID] = useState<number | undefined>(undefined);
    const { visible } = props;

    return (
        <div
            className={
                'flex-col w-full h-full overflow-y-scroll gap-y-4 py-4 ' +
                (visible ? 'flex ' : 'hidden ')
            }
        >
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
