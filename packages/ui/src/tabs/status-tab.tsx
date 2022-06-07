import { useState } from 'react';
import TYPES from '../utils/types';

import PyraCoreStatus from '../components/status/pyra-core-status';
import MeasurementDecisionStatus from '../components/status/measurement-decision-status';

export default function StatusTab(props: {
    visible: boolean;
    centralConfig: TYPES.config;
    setCentralConfig(c: TYPES.config): void;
}) {
    // "undefined" indicates that the pyra-core state is currently
    // being checked, "-1" indicates that pyra-core is not running
    const [pyraCorePID, setPyraCorePID] = useState<number | undefined>(undefined);

    const { visible, centralConfig, setCentralConfig } = props;

    // TODO: Move central config to redux store
    // TODO: Pull state and central config in regular time intervals (only when pyra is running)

    return (
        <div
            className={
                'flex-col w-full h-full gap-y-4 py-4 ' + (visible ? 'flex ' : 'hidden ')
            }
        >
            <PyraCoreStatus {...{ pyraCorePID, setPyraCorePID }} />
            <div className="w-full h-px bg-slate-300" />
            {pyraCorePID !== undefined && pyraCorePID !== -1 && (
                <>
                    <MeasurementDecisionStatus
                        {...{ centralConfig, setCentralConfig }}
                    />
                    <div className="w-full h-px bg-slate-300" />
                </>
            )}
        </div>
    );
}
