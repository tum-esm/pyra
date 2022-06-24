import { useState } from 'react';
import { customTypes } from '../../custom-types';
import { backend, reduxUtils } from '../../utils';
import { essentialComponents } from '..';
import { ICONS } from '../../assets';

function formatTime(t: { hour: number; minute: number; second: number }) {
    return (
        `${t.hour < 10 ? '0' : ''}${t.hour}:` +
        `${t.minute < 10 ? '0' : ''}${t.minute}:` +
        `${t.second < 10 ? '0' : ''}${t.second}`
    );
}

function CLIModeInfo() {
    return (
        <div className="w-full px-6 text-xs text-gray-900 flex-row-left-top gap-x-2">
            <div className="flex-row-center">
                <div className="w-4 h-4 mr-1 text-gray-600">{ICONS.info}</div>
                <span>
                    Sending manual decisions via the command line. Read about "cli mode" in the Pyra
                    4 documentation
                </span>
            </div>
        </div>
    );
}
function MeasurementTriggerInfo() {
    const measurementTriggers = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_triggers
    );
    const centralConfigVBDSD = reduxUtils.useTypedSelector((s) => s.config.central?.vbdsd);

    if (measurementTriggers === undefined || centralConfigVBDSD === undefined) {
        return <></>;
    }
    return (
        <div className="w-full px-6 text-sm text-gray-700 flex-row-left-top gap-x-2">
            <div className="flex-row-center">
                <div className="w-4 h-4 mr-1">{ICONS.info}</div>Automatic decision based on:
            </div>
            <div className="flex flex-col gap-y-1">
                {[
                    [
                        measurementTriggers.consider_time,
                        'Time [H:M:S]',
                        <>
                            {measurementTriggers.consider_time
                                ? `from ${formatTime(
                                      measurementTriggers.start_time
                                  )} to ${formatTime(measurementTriggers.stop_time)}`
                                : 'ignored'}
                        </>,
                    ],
                    [
                        measurementTriggers.consider_sun_elevation,
                        'Sun Elevation',
                        <>
                            {measurementTriggers.consider_sun_elevation
                                ? `from ${measurementTriggers.min_sun_elevation}° to ${measurementTriggers.max_sun_elevation}°`
                                : 'ignored'}
                        </>,
                    ],
                    [
                        measurementTriggers.consider_vbdsd,
                        'VBDSD Result',
                        <>
                            {!measurementTriggers.consider_vbdsd && 'ignored'}
                            {measurementTriggers.consider_vbdsd && centralConfigVBDSD === null && (
                                <span className="text-red-500 uppercase">not configured!</span>
                            )}
                            {measurementTriggers.consider_vbdsd &&
                                centralConfigVBDSD !== null &&
                                `from ${formatTime(measurementTriggers.start_time)} to ${formatTime(
                                    measurementTriggers.stop_time
                                )}`}
                        </>,
                    ],
                ].map((row: any, i) => (
                    <div
                        className={
                            'flex-row-left ' +
                            (row[0]
                                ? 'text-gray-700 font-semibold'
                                : 'text-gray-400 line-through font-normal')
                        }
                    >
                        <div className="w-28">{row[1]}</div>
                        <div>{row[2]}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function MeasurementDecisionStatus() {
    const measurementDecision = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_decision
    );
    const manualMeasurementDecisionResult = reduxUtils.useTypedSelector(
        (s) => s.coreState.content?.automation_should_be_running
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
            measurementDecisionResult = manualMeasurementDecisionResult;
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
        <div className="flex flex-col gap-y-1">
            <div className="flex w-full px-6 text-sm gap-x-2">
                <div className="text-sm font-normal h-7 flex-row-left">
                    <essentialComponents.Ping
                        state={loading ? undefined : measurementDecisionResult}
                    />
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
            {measurementDecision.mode === 'automatic' && <MeasurementTriggerInfo />}
            {measurementDecision.mode === 'cli' && <CLIModeInfo />}
        </div>
    );
}
