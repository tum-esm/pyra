import { reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import ICONS from '../assets/icons';

export default function OverviewTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.body);
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    const measurementDecision = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_decision
    );
    const automaticMeasurementDecisionResult = reduxUtils.useTypedSelector(
        (s) => s.coreState.body?.measurements_should_be_running
    );
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

    // TODO: Implement plc readings + close cover
    // TODO: Implement system stats

    const allInfoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);
    const currentInfoLogLines =
        allInfoLogLines === undefined ? ['...'] : allInfoLogLines.slice(-10);

    return (
        <div className={'flex-col-center w-full h-full overflow-y-scroll gap-y-4 pt-4 pb-12 px-6'}>
            <div className="w-full text-sm h-7 flex-row-left">
                <essentialComponents.Ping state={true} />
                <span className="ml-2.5 mr-1">
                    pyra-core is running with process ID {pyraCorePID}
                </span>
            </div>
            <div className="w-full -mt-2 text-sm font-normal flex-row-left">
                <essentialComponents.Ping state={measurementDecisionResult} />
                <span className="ml-2.5 mr-1">Measurements are currently</span>
                {measurementDecisionResult === undefined && <essentialComponents.Spinner />}
                {!(measurementDecisionResult === undefined) && (
                    <>
                        {!measurementDecisionResult && <>not running</>}
                        {measurementDecisionResult && <>running</>}
                    </>
                )}
                {measurementDecision?.mode !== undefined && (
                    <strong className="ml-1 font-semibold">
                        ({measurementDecision.mode} mode)
                    </strong>
                )}
            </div>
            <div className="w-full h-px bg-gray-300" />
            {coreState === undefined && (
                <div className="w-full flex-row-left gap-x-2">
                    State is loading <essentialComponents.Spinner />
                </div>
            )}
            {coreState?.enclosure_plc_readings.state.rain === true &&
                coreState?.enclosure_plc_readings.state.cover_closed === false && (
                    <div
                        className={
                            'w-full py-1 pl-2 pr-3 flex-row-left gap-x-1 shadow-sm ' +
                            'bg-red-600 rounded-md text-red-50 text-sm font-semibold ' +
                            'border border-red-900 -mb-2 '
                        }
                    >
                        <div className="w-6 h-6 p-[0.075rem] text-white">{ICONS.alert}</div>
                        Rain was detected but cover is not closed!
                    </div>
                )}
            {coreState !== undefined && (
                <div className="grid w-full grid-cols-2 divide-x divide-gray-300">
                    <div className="pr-2 text-sm flex-col-left gap-y-1">
                        {[
                            {
                                label: 'Temperature',
                                value: coreState.enclosure_plc_readings.sensors.temperature,
                            },
                            {
                                label: 'Reset needed',
                                value: coreState.enclosure_plc_readings.state.reset_needed,
                            },
                            {
                                label: 'Motor failed',
                                value: coreState.enclosure_plc_readings.state.motor_failed,
                            },
                            {
                                label: 'Cover is closed',
                                value: coreState.enclosure_plc_readings.state.cover_closed,
                            },
                            {
                                label: 'Rain Detected',
                                value: coreState.enclosure_plc_readings.state.rain,
                            },
                        ].map((s) => (
                            <div className="w-full pl-2 flex-row-left">
                                <div className="w-32">{s.label}:</div>
                                <div>{s.value || '-'}</div>
                            </div>
                        ))}
                        <essentialComponents.Button
                            variant="red"
                            onClick={() => {}}
                            className="w-full mt-1"
                        >
                            force cover close
                        </essentialComponents.Button>
                    </div>
                    <div className="pl-2 flex-col-left">fghj</div>
                </div>
            )}
            <div>system stats: {JSON.stringify(coreState)}</div>
            <div className="w-full h-px bg-gray-300" />
            <div className="w-full font-medium">Last 10 log lines:</div>
            <pre
                className={
                    'w-full py-2 !mb-0 overflow-x-auto bg-white flex-grow ' +
                    'border border-gray-250 shadow-sm rounded-md -mt-2'
                }
            >
                <code className="w-full h-full !text-xs">
                    {currentInfoLogLines.map((l, i) => (
                        <essentialComponents.LogLine key={`${i} ${l}`} text={l} />
                    ))}
                </code>
            </pre>
        </div>
    );
}
