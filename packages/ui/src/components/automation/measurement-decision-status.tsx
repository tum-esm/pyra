import { useState } from 'react';
import { customTypes } from '../../custom-types';
import { fetchUtils, reduxUtils } from '../../utils';
import { essentialComponents } from '..';
import { ICONS } from '../../assets';
import toast from 'react-hot-toast';

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
                        </>,
                    ],
                ].map((row: any, i) => (
                    <div
                        key={i}
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
    const automaticMeasurementDecisionResult = reduxUtils.useTypedSelector(
        (s) => s.coreState.body?.measurements_should_be_running
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
            measurementDecisionResult = automaticMeasurementDecisionResult;
            break;
    }

    async function updateMeasurementDecisionMode(mode: 'automatic' | 'manual' | 'cli') {
        setLoading(true);
        let update: customTypes.partialConfig;
        if (mode === 'manual') {
            // when switching from cli/automatic to manual, the
            // measurements should continue running/not running
            update = {
                measurement_decision: {
                    mode,
                    manual_decision_result: automaticMeasurementDecisionResult || false,
                },
            };
        } else {
            // when switching to automatic the current measurement decision will be kept anyways
            // when switching to cli mode, the decision in the config will be used right away
            update = {
                measurement_decision: { mode },
            };
        }
        const result = await fetchUtils.backend.updateConfig(update);
        if (result.stdout.includes('Updated config file')) {
            setConfigsPartial(update);
        } else {
            console.error(
                `Could not update config file. processResult = ${JSON.stringify(result)}`
            );
            toast.error(`Could not update config file, please look in the console for details`);
        }
        setLoading(false);
    }

    async function updateManualMeasurementDecisionResult(decisionResult: boolean) {
        setLoading(true);
        const update = { measurement_decision: { manual_decision_result: decisionResult } };
        const result = await fetchUtils.backend.updateConfig(update);
        if (result.stdout.includes('Updated config file')) {
            setConfigsPartial(update);
        } else {
            console.error(
                `Could not update config file. processResult = ${JSON.stringify(result)}`
            );
            toast.error(`Could not update config file, please look in the console for details`);
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
                    {(loading || measurementDecisionResult === undefined) && (
                        <div className="w-4 h-4 text-gray-700 animate-spin">{ICONS.spinner}</div>
                    )}
                    {!(loading || measurementDecisionResult === undefined) && (
                        <>
                            {!measurementDecisionResult && <>not running</>}
                            {measurementDecisionResult && <>running</>}
                        </>
                    )}
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
                                'h-7 flex-row-center font-normal w-full text-gray-500 text-center'
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
                                    ? 'gray'
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
