import { IconMicroscope } from '@tabler/icons-react';
import { useState } from 'react';
import { Button } from '../ui/button';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';
import { fetchUtils } from '../../utils';
import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { renderTimeObject } from '../../utils/functions';

function ModePanel(props: {
    label: string;
    isActive: boolean;
    onClick: () => void;
    children: React.ReactNode;
}) {
    if (props.isActive) {
        return (
            <div className="flex flex-col p-3 bg-white border rounded-lg text-slate-900 border-slate-200 gap-y-2">
                <strong className="w-full font-semibold text-center">{props.label} Mode</strong>
                {props.children}
            </div>
        );
    } else {
        return (
            <button
                onClick={props.onClick}
                className="flex flex-col items-start justify-start p-3 text-left border rounded-lg gap-y-2 bg-slate-100 text-slate-400 border-slate-200"
            >
                <strong className="w-full font-semibold text-center">{props.label} Mode</strong>
                {props.children}
            </button>
        );
    }
}

export default function MeasurementDecision() {
    const [activeMode, setActiveMode] = useState('automatic');
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { centralConfig, setConfigItem } = useConfigStore();
    const { coreState } = useCoreStateStore();

    function toggleManualMeasurementMode() {
        if (centralConfig) {
            const newDecisionResult = !centralConfig.measurement_decision.manual_decision_result;
            runPromisingCommand({
                command: () =>
                    fetchUtils.backend.updateConfig({
                        measurement_decision: {
                            manual_decision_result: !newDecisionResult,
                        },
                    }),
                label: 'toggling manual measurement mode',
                successLabel:
                    'successfully toggled manual measurement mode, system will react soon',
                onSuccess: () => {
                    setConfigItem('measurement_decision.manual_decision_result', newDecisionResult);
                },
            });
        }
    }
    if (!centralConfig || !coreState) {
        return <></>;
    }

    let automaticFilterSettingsConsidered: string[] = [];
    let automaticFilterSettingsNotConsidered: string[] = [];

    if (centralConfig.measurement_triggers.consider_sun_elevation) {
        automaticFilterSettingsConsidered.push(
            `sun elevation is above ${centralConfig.measurement_triggers.min_sun_elevation}°`
        );
    } else {
        automaticFilterSettingsNotConsidered.push('sun elevation');
    }
    if (centralConfig.measurement_triggers.consider_time) {
        automaticFilterSettingsConsidered.push(
            `time is between ${renderTimeObject(
                centralConfig.measurement_triggers.start_time
            )} and ${renderTimeObject(centralConfig.measurement_triggers.stop_time)}`
        );
    } else {
        automaticFilterSettingsNotConsidered.push('time');
    }
    if (centralConfig.measurement_triggers.consider_helios) {
        automaticFilterSettingsConsidered.push(`Helios is detects good conditions`);
    } else {
        automaticFilterSettingsNotConsidered.push('Helios');
    }

    return (
        <div className="flex flex-col w-full gap-y-2">
            <div
                className={
                    'flex flex-row items-center w-full p-3 font-medium text-green-900 bg-green-300 rounded-lg gap-x-2 ' +
                    (coreState.measurements_should_be_running === null
                        ? 'text-slate-900 bg-slate-200'
                        : coreState.measurements_should_be_running
                        ? 'text-green-900 bg-green-300'
                        : 'text-yellow-900 bg-yellow-300')
                }
            >
                <IconMicroscope size={20} />
                <div>
                    {coreState.measurements_should_be_running === null ? (
                        centralConfig.general.test_mode ? (
                            'not running any measurements in test mode'
                        ) : (
                            'system is starting up'
                        )
                    ) : (
                        <>
                            System is currently{' '}
                            {!coreState.measurements_should_be_running && <strong>not</strong>}{' '}
                            measuring
                        </>
                    )}
                </div>
            </div>
            <div className="grid grid-cols-3 gap-x-2">
                <ModePanel
                    label="Automatic"
                    isActive={activeMode === 'automatic'}
                    onClick={() => setActiveMode('automatic')}
                >
                    {activeMode === 'automatic' && (
                        <div>
                            Read more about this in the{' '}
                            {activeMode === 'automatic' ? (
                                <a
                                    href="https://pyra.esm.ei.tum.de/docs/user-guide/measurements/#measurement-modes-and-triggers"
                                    target="_blank"
                                    className="text-blue-500 underline"
                                >
                                    Pyra Docs
                                </a>
                            ) : (
                                <span className="text-blue-300 underline">Pyra Docs</span>
                            )}
                            .
                        </div>
                    )}
                </ModePanel>
                <ModePanel
                    label="Manual"
                    isActive={activeMode === 'manual'}
                    onClick={() => setActiveMode('manual')}
                >
                    {activeMode === 'manual' && (
                        <div>
                            Current state:{' '}
                            <strong>
                                {centralConfig.measurement_decision.manual_decision_result
                                    ? 'measuring'
                                    : 'not measuring'}
                            </strong>
                        </div>
                    )}
                    {activeMode === 'manual' && (
                        <Button className="w-full" onClick={toggleManualMeasurementMode}>
                            {centralConfig.measurement_decision.manual_decision_result
                                ? 'Stop'
                                : 'Start'}{' '}
                            Measurements
                        </Button>
                    )}
                </ModePanel>
                <ModePanel
                    label="CLI"
                    isActive={activeMode === 'cli'}
                    onClick={() => setActiveMode('cli')}
                >
                    {activeMode === 'cli' && (
                        <>
                            <div>
                                Current state:{' '}
                                <strong>
                                    {centralConfig.measurement_decision.cli_decision_result
                                        ? 'measuring'
                                        : 'not measuring'}
                                </strong>
                            </div>
                            <div>
                                Read more about this in the{' '}
                                {activeMode === 'cli' ? (
                                    <a
                                        href="https://pyra.esm.ei.tum.de/docs/user-guide/measurements#starting-and-stopping-measurements-via-cli"
                                        target="_blank"
                                        className="text-blue-500 underline"
                                    >
                                        Pyra Docs
                                    </a>
                                ) : (
                                    <span className="text-blue-300 underline">Pyra Docs</span>
                                )}
                                .
                            </div>
                        </>
                    )}
                </ModePanel>
            </div>
        </div>
    );
}
