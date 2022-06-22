import { useState } from 'react';
import backend from '../../utils/backend';
import TYPES from '../../utils/types';
import { defaultsDeep } from 'lodash';
import Button from '../essential/button';
import Toggle from '../essential/toggle';
import Ping from '../essential/ping';
import ICONS from '../../assets/icons';

export default function MeasurementDecisionStatus(props: {
    centralConfig: TYPES.config;
    setCentralConfig(c: TYPES.config): void;
}) {
    const { centralConfig, setCentralConfig } = props;
    const [loading, setLoading] = useState(false);

    const measurementDecision = centralConfig.measurement_decision;

    let measurementDecisionResult = undefined;
    if (measurementDecision.mode === 'manual') {
        measurementDecisionResult = measurementDecision.manual_decision_result;
    }
    // TODO: integrate cli and automatic decision result

    async function updateMeasurementDecisionMode(mode: 'automatic' | 'manual' | 'cli') {
        setLoading(true);
        const update = {
            measurement_decision: { mode, manual_decision_result: false },
        };
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
        setLoading(false);
    }

    async function updateManualMeasurementDecisionResult(result: boolean) {
        setLoading(true);
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
        setLoading(false);
    }

    return (
        <div className={'w-full text-sm flex gap-x-2 px-6'}>
            <div className="text-sm font-normal h-7 flex-row-left">
                <Ping state={loading ? undefined : measurementDecisionResult} />
                <span className="ml-2.5 mr-1">Measurements are currently</span>
                {loading && (
                    <div className="w-4 h-4 text-gray-700 animate-spin">
                        {ICONS.spinner}
                    </div>
                )}
                {!loading && !measurementDecisionResult && 'not running'}
                {!loading && measurementDecisionResult && 'running'}
            </div>
            <div className="flex-grow" />
            <div className="flex-col-center gap-y-2">
                <Toggle
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
                    <Button
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
                        spinner={loading}
                    >
                        {measurementDecision.manual_decision_result ? 'stop' : 'start'}
                    </Button>
                )}
            </div>
        </div>
    );
}
