import backend from '../../utils/backend';
import TYPES from '../../utils/types';
import { defaultsDeep } from 'lodash';

export default function MeasurementDecisionStatus(props: {
    centralConfig: TYPES.config;
    setCentralConfig(c: TYPES.config): void;
}) {
    const { centralConfig, setCentralConfig } = props;

    const measurementDecision = centralConfig.measurement_decision;

    let mesurementDecisionResult = undefined;
    if (measurementDecision.mode === 'manual') {
        mesurementDecisionResult = measurementDecision.manual_decision_result;
    }
    // TODO: add cli and automatic decision result

    async function updateMeasurementDecisionMode(mode: 'automatic' | 'manual' | 'cli') {
        const update = { measurement_decision: { mode } };
        const newCentralConfig = defaultsDeep(
            update,
            JSON.parse(JSON.stringify(centralConfig))
        );
        const p = await backend.updateConfig(update);
        if (p.stdout.includes('Updated config file')) {
            setCentralConfig(newCentralConfig);
        } else {
            // TODO: add message to queue
        }
    }

    async function updateManualMeasurementDecisionResult(result: boolean) {
        const update = { measurement_decision: { manual_decision_result: result } };
        const newCentralConfig = defaultsDeep(
            update,
            JSON.parse(JSON.stringify(centralConfig))
        );
        const p = await backend.updateConfig(update);
        if (p.stdout.includes('Updated config file')) {
            setCentralConfig(newCentralConfig);
        } else {
            // TODO: add message to queue
        }
    }

    return (
        <div
            className={
                'w-full text-sm bg-white border border-gray-300 ' +
                'rounded-md shadow-sm flex-row-left'
            }
        >
            <div className="px-3 font-normal flex-row-left">
                Measurements are{' '}
                <span className="ml-1 mr-4">
                    {!mesurementDecisionResult && (
                        <span className="font-semibold text-red-600">not running</span>
                    )}
                    {mesurementDecisionResult && (
                        <>
                            <span className="font-semibold text-green-600">
                                running
                            </span>
                        </>
                    )}
                </span>
            </div>
            <div className="flex-grow" />
            <div className="flex flex-col">
                <div className="flex flex-row">
                    {['automatic', 'manual', 'cli'].map((m: any) => (
                        <button
                            onClick={() =>
                                measurementDecision.mode !== m
                                    ? updateMeasurementDecisionMode(m)
                                    : {}
                            }
                            className={
                                'px-3 py-1.5 last:rounded-tr-md border-l border-b border-gray-300 font-medium w-32 flex-row-center ' +
                                (measurementDecision.mode === m
                                    ? 'bg-blue-200 text-blue-950 '
                                    : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-950 ')
                            }
                        >
                            <div
                                className={
                                    'w-2 h-2 mr-1 rounded-full ' +
                                    (measurementDecision.mode === m
                                        ? 'bg-blue-800 '
                                        : 'bg-gray-300')
                                }
                            />
                            {m}
                        </button>
                    ))}
                </div>
                {measurementDecision.mode !== 'manual' && (
                    <div
                        className={
                            'px-3 py-1.5 border-l border-gray-300 font-light w-full ' +
                            'bg-gray-50 text-gray-500 text-center rounded-br-md'
                        }
                    >
                        automated decision
                    </div>
                )}
                {measurementDecision.mode === 'manual' && (
                    <button
                        onClick={() =>
                            updateManualMeasurementDecisionResult(
                                !measurementDecision.manual_decision_result
                            )
                        }
                        className={
                            'px-3 py-1.5 border-l border-gray-300 font-medium w-full rounded-br-md ' +
                            (!measurementDecision.manual_decision_result
                                ? 'bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-900 '
                                : 'bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-900 ')
                        }
                    >
                        {measurementDecision.manual_decision_result ? 'stop' : 'start'}
                    </button>
                )}
            </div>
        </div>
    );
}
