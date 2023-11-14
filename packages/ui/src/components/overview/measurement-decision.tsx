import {
    IconPlayerPauseFilled,
    IconPlayerPlayFilled,
    IconRobot,
    IconToggleRight,
    IconWand,
} from '@tabler/icons-react';
import { Button } from '../ui/button';
import { useConfigStore } from '../../utils/zustand-utils/config-zustand';
import { fetchUtils } from '../../utils';
import { useCoreStateStore } from '../../utils/zustand-utils/core-state-zustand';
import { renderTimeObject } from '../../utils/functions';

function ModePanel(props: {
    icon: React.ReactNode;
    label: string;
    isActive: boolean;
    onClick: () => void;
    children?: React.ReactNode;
}) {
    if (props.isActive) {
        return (
            <div className="flex flex-col p-3 bg-white border rounded-lg text-slate-900 border-slate-200 gap-y-2">
                <strong className="flex flex-row items-center justify-center w-full font-semibold text-center gap-x-2">
                    {props.icon}
                    <div>{props.label} Mode</div>
                </strong>
                {props.children}
            </div>
        );
    } else {
        return (
            <button
                onClick={props.onClick}
                className="flex flex-col items-start justify-start p-3 text-left border rounded-lg gap-y-2 bg-slate-100 text-slate-400 border-slate-200"
            >
                <strong className="flex flex-row items-center justify-center w-full font-semibold text-center gap-x-2">
                    {props.icon}
                    <div>{props.label} Mode</div>
                </strong>
            </button>
        );
    }
}

export default function MeasurementDecision() {
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { centralConfig, setConfigItem } = useConfigStore();
    const { coreState } = useCoreStateStore();
    const activeMode = centralConfig?.measurement_decision.mode;

    function setActiveMode(mode: 'automatic' | 'manual' | 'cli') {
        if (centralConfig) {
            runPromisingCommand({
                command: () =>
                    fetchUtils.backend.updateConfig({
                        measurement_decision: {
                            mode: mode,
                        },
                    }),
                label: 'setting measurement mode',
                successLabel: 'successfully set measurement mode, system will react soon',
                onSuccess: () => {
                    setConfigItem('measurement_decision.mode', mode);
                },
            });
        }
    }
    if (!centralConfig || !coreState) {
        return <></>;
    }

    function toggleManualMeasurementDecision() {
        if (centralConfig) {
            const newDecisionResult = !centralConfig.measurement_decision.manual_decision_result;
            runPromisingCommand({
                command: () =>
                    fetchUtils.backend.updateConfig({
                        measurement_decision: {
                            manual_decision_result: newDecisionResult,
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
        <div className="grid w-full grid-cols-3 gap-x-2">
            <ModePanel
                icon={<IconWand size={18} />}
                label="Automatic"
                isActive={activeMode === 'automatic'}
                onClick={() => setActiveMode('automatic')}
            />
            <ModePanel
                icon={<IconToggleRight size={18} />}
                label="Manual"
                isActive={activeMode === 'manual'}
                onClick={() => setActiveMode('manual')}
            >
                {activeMode === 'manual' && (
                    <div className="flex flex-row items-center w-full h-8">
                        <div>
                            Current state:{' '}
                            <strong>
                                {centralConfig.measurement_decision.manual_decision_result
                                    ? 'measuring'
                                    : 'not measuring'}
                            </strong>
                        </div>
                        <div className="flex-grow" />
                        <button
                            className="flex items-center justify-center w-8 h-8 rounded-lg shadow text-slate-50 bg-slate-900 hover:bg-slate-800 hover:text-white"
                            onClick={toggleManualMeasurementDecision}
                        >
                            {centralConfig.measurement_decision.manual_decision_result ? (
                                <IconPlayerPauseFilled size={18} />
                            ) : (
                                <IconPlayerPlayFilled size={18} />
                            )}
                        </button>
                    </div>
                )}
            </ModePanel>
            <ModePanel
                icon={<IconRobot size={18} />}
                label="CLI"
                isActive={activeMode === 'cli'}
                onClick={() => setActiveMode('cli')}
            >
                {activeMode === 'cli' && (
                    <div className="flex flex-row items-center w-full h-8">
                        <div>
                            Current state:{' '}
                            <strong>
                                {centralConfig.measurement_decision.cli_decision_result
                                    ? 'measuring'
                                    : 'not measuring'}
                            </strong>
                        </div>
                    </div>
                )}
            </ModePanel>
        </div>
    );
}
