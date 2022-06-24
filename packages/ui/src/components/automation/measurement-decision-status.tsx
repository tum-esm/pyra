import { useState } from 'react';
import { customTypes } from '../../custom-types';
import { backend, reduxUtils } from '../../utils';
import { essentialComponents } from '..';
import { ICONS } from '../../assets';

export default function MeasurementDecisionStatus() {
    const measurementDecision = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_decision
    );
    const dispatch = reduxUtils.useTypedDispatch();
    const setConfigsPartial = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setConfigsPartial(c));

    const [loading, setLoading] = useState(false);

    let measurementDecisionResult: boolean | undefined = undefined;
    switch (measurementDecision?.mode) {
        case 'manual':
            measurementDecisionResult = measurementDecision.manual_decision_result;
            break;
        case 'cli':
            measurementDecisionResult = measurementDecision.cli_decision_result;
            break;
        case 'automatic':
            // TODO: Use state.json
            break;
    }

    async function updateMeasurementDecisionMode(mode: 'automatic' | 'manual' | 'cli') {
        setLoading(true);
        const update = {
            measurement_decision: { mode, manual_decision_result: false },
        };
        const p = await backend.updateConfig(update);
        if (p.stdout.includes('Updated config file')) {
            setConfigsPartial(update);
        } else {
            // TODO: add message to queue
        }
        setLoading(false);
    }

    async function updateManualMeasurementDecisionResult(result: boolean) {
        setLoading(true);
        const update = { measurement_decision: { manual_decision_result: result } };
        const p = await backend.updateConfig(update);
        if (p.stdout.includes('Updated config file')) {
            setConfigsPartial(update);
        } else {
            // TODO: add message to queue
        }
        setLoading(false);
    }

    if (measurementDecision === undefined) {
        return <></>;
    }

    return (
        <div className={'w-full text-sm flex gap-x-2 px-6'}>
            <div className="text-sm font-normal h-7 flex-row-left">
                <essentialComponents.Ping state={loading ? undefined : measurementDecisionResult} />
                <span className="ml-2.5 mr-1">Measurements are currently</span>
                {loading && (
                    <div className="w-4 h-4 text-gray-700 animate-spin">{ICONS.spinner}</div>
                )}
                {!loading && !measurementDecisionResult && <>not running</>}
                {!loading && measurementDecisionResult && <>running</>}
            </div>
            <div className="flex-grow" />
            <div className="flex-col-center gap-y-2">
                <essentialComponents.Toggle
                    value={measurementDecision.mode}
                    values={['automatic', 'manual', 'cli']}
                    className="w-28"
                    setValue={updateMeasurementDecisionMode}
                />
                {measurementDecision.mode !== 'manual' && (
                    <div
                        className={
                            'h-7 flex-row-center font-normal w-full text-slate-500 text-center'
                        }
                    >
                        automated decision
                    </div>
                )}
                {measurementDecision.mode === 'manual' && (
                    <essentialComponents.Button
                        onClick={() =>
                            updateManualMeasurementDecisionResult(
                                !measurementDecision.manual_decision_result
                            )
                        }
                        className="w-full"
                        variant={
                            loading
                                ? 'slate'
                                : measurementDecision.manual_decision_result
                                ? 'red'
                                : 'green'
                        }
                        disabled={loading}
                    >
                        {measurementDecision.manual_decision_result ? 'stop' : 'start'}
                    </essentialComponents.Button>
                )}
            </div>
        </div>
    );
}
