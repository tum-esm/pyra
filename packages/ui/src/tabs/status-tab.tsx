import { useEffect, useState } from 'react';
import backend from '../utils/backend';
import TYPES from '../utils/types';

export default function StatusTab(props: {
    visible: boolean;
    centralConfig: TYPES.config;
    setCentralConfig(c: TYPES.config): void;
}) {
    // undefined indicates that the pyra-core state has not been checked yet
    // -1 indicates that pyra-core is not running
    const [pyraCorePID, setPyraCorePID] = useState<number | undefined>(undefined);
    const [pyraCoreStateIsPending, setPyraCoreStateIsPending] = useState(false);

    const [measurementDecisionMode, setMeasurementDecisionMode] = useState(
        props.centralConfig.measurement_decision.mode
    );
    const [manualMeasurementDecisionResult, setManualMeasurementDecisionResult] =
        useState(props.centralConfig.measurement_decision.manual_decision_result);

    async function updatePyraCoreIsRunning() {
        const p = await backend.checkPyraCoreState();
        if (p.stdout.includes('pyra-core is running with PID')) {
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setPyraCorePID(pid);
        } else {
            setPyraCorePID(-1);
        }
    }
    useEffect(() => {
        updatePyraCoreIsRunning();
    }, []);

    async function updateMeasurementDecisionMode(
        newMode: 'automatic' | 'manual' | 'cli'
    ) {
        const p = await backend.updateConfig({
            measurement_decision: { mode: newMode },
        });
        if (p.stdout.includes('Updated config file')) {
            setMeasurementDecisionMode(newMode);
        } else {
            // TODO: add message to queue
        }
    }

    async function startPyraCore() {
        setPyraCoreStateIsPending(true);
        const p = await backend.startPyraCore();
        const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
        // TODO: add message to queue
        setPyraCorePID(pid);
        setPyraCoreStateIsPending(false);
    }

    async function stopPyraCore() {
        setPyraCoreStateIsPending(true);
        await backend.stopPyraCore();
        setPyraCorePID(-1);
        setPyraCoreStateIsPending(false);
    }

    return (
        <div
            className={
                'flex-col w-full h-full p-6 gap-y-4 ' +
                (props.visible ? 'flex ' : 'hidden ')
            }
        >
            {pyraCorePID !== undefined && (
                <div
                    className={
                        'w-full text-sm bg-white border border-gray-300 ' +
                        'rounded-md shadow-sm flex-row-left'
                    }
                >
                    <div className="px-3 font-normal flex-row-left">
                        pyra-core is{' '}
                        {pyraCoreStateIsPending && (
                            <span className="ml-1 mr-4 font-semibold">...</span>
                        )}
                        {!pyraCoreStateIsPending && (
                            <span className="ml-1 mr-4">
                                {pyraCorePID === -1 && (
                                    <span className="font-semibold text-red-600">
                                        not running
                                    </span>
                                )}
                                {pyraCorePID !== -1 && (
                                    <>
                                        <span className="font-semibold text-green-600">
                                            running
                                        </span>{' '}
                                        with process ID {pyraCorePID}
                                    </>
                                )}
                            </span>
                        )}
                    </div>
                    <div className="flex-grow" />
                    <button
                        onClick={pyraCorePID === -1 ? startPyraCore : stopPyraCore}
                        className={
                            'px-3 py-1.5 rounded-r-md border-l border-gray-300 font-medium w-16 ' +
                            (pyraCorePID === -1
                                ? 'bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-900 '
                                : 'bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-900 ')
                        }
                    >
                        {pyraCorePID === -1 ? 'start' : 'stop'}
                    </button>
                </div>
            )}
            <div
                className={
                    'w-full text-sm bg-white border border-gray-300 ' +
                    'rounded-md shadow-sm flex-row-left'
                }
            >
                <div className="px-3 font-normal flex-row-left">
                    Measurement decision:
                </div>
                <div className="flex-grow" />
                <div className="flex flex-col">
                    <div className="flex flex-row">
                        {['automatic', 'manual', 'cli'].map((m: any) => (
                            <button
                                onClick={() =>
                                    measurementDecisionMode !== m
                                        ? updateMeasurementDecisionMode(m)
                                        : {}
                                }
                                className={
                                    'px-3 py-1.5 last:rounded-tr-md border-l border-b border-gray-300 font-medium w-32 flex-row-center ' +
                                    (measurementDecisionMode === m
                                        ? 'bg-blue-200 text-blue-950 '
                                        : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-950 ')
                                }
                            >
                                <div
                                    className={
                                        'w-2 h-2 mr-1 rounded-full ' +
                                        (measurementDecisionMode === m
                                            ? 'bg-blue-800 '
                                            : 'bg-gray-300')
                                    }
                                />
                                {m}
                            </button>
                        ))}
                    </div>
                    {measurementDecisionMode !== 'manual' && (
                        <div
                            className={
                                'px-3 py-1.5 border-l border-gray-300 font-light w-full ' +
                                'bg-gray-50 text-gray-500 text-center rounded-br-md'
                            }
                        >
                            automated decision
                        </div>
                    )}
                    {measurementDecisionMode === 'manual' && (
                        <button
                            className={
                                'px-3 py-1.5 border-l border-gray-300 font-medium w-full rounded-br-md ' +
                                (true
                                    ? 'bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-900 '
                                    : 'bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-900 ')
                            }
                        >
                            "start/stop"
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
