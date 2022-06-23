import { useEffect, useState } from 'react';
import TYPES from '../utils/types';

import PyraCoreStatus from '../components/status/pyra-core-status';
import MeasurementDecisionStatus from '../components/status/measurement-decision-status';
import EnclosureStatus from '../components/status/enclosure-status';
import backend from '../utils/backend';
import { watch } from 'tauri-plugin-fs-watch-api';

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

    const [centralState, setCentralState] = useState(undefined);
    const [centralStateloadingIsPending, setCentralStateLoadingIsPending] =
        useState(true);

    async function loadCentralState() {
        setCentralStateLoadingIsPending(false);
        const p = await backend.getState();
        try {
            setCentralState(JSON.parse(p.stdout));
        } catch {
            // TODO: Add message to queue
        }
    }

    useEffect(() => {
        initializeFileWatcher();
    }, []);

    useEffect(() => {
        if (centralStateloadingIsPending) {
            loadCentralState();
        }
    }, [centralStateloadingIsPending, loadCentralState]);

    async function initializeFileWatcher() {
        let stateFilePath =
            import.meta.env.VITE_PROJECT_DIR + '\\runtime-data\\state.json';
        if (window.navigator.platform.includes('Mac')) {
            stateFilePath = stateFilePath.replace(/\\/g, '/');
        }
        await watch(stateFilePath, { recursive: false }, (o) =>
            setCentralStateLoadingIsPending(o.type === 'Write')
        );
    }

    return (
        <div
            className={
                'flex-col w-full h-full overflow-y-scroll gap-y-4 py-4 ' +
                (visible ? 'flex ' : 'hidden ')
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
                    <EnclosureStatus centralState={centralState} />
                </>
            )}
        </div>
    );
}
