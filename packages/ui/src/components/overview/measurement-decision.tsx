import { IconMicroscope } from '@tabler/icons-react';
import { useState } from 'react';
import { Button } from '../ui/button';

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
    const [measurementsAreRunning, setMeasurementsAreRunning] = useState(false);

    return (
        <div className="flex flex-col w-full gap-y-2">
            <div
                className={
                    'flex flex-row items-center w-full p-3 font-medium text-green-900 bg-green-300 rounded-lg gap-x-2 ' +
                    (measurementsAreRunning
                        ? 'text-green-900 bg-green-300'
                        : 'text-yellow-900 bg-yellow-300')
                }
            >
                <IconMicroscope size={20} />
                <div>
                    System is currently {!measurementsAreRunning && <strong>not</strong>} measuring
                </div>
            </div>
            <div className="grid grid-cols-3 gap-x-2">
                <ModePanel
                    label="Automatic"
                    isActive={activeMode === 'automatic'}
                    onClick={() => setActiveMode('automatic')}
                >
                    <div>
                        <strong>Current filter settings:</strong>{' '}
                        <em>
                            Measuring if time is between 07:00:00 and 21:00:00 <strong>and</strong>{' '}
                            sun angle is above 10°. Not considering Helios.
                        </em>
                    </div>

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
                </ModePanel>
                <ModePanel
                    label="Manual"
                    isActive={activeMode === 'manual'}
                    onClick={() => setActiveMode('manual')}
                >
                    Manually start and stop measurements here.
                    {activeMode === 'manual' ? (
                        <Button
                            className="w-full"
                            onClick={() => setMeasurementsAreRunning(!measurementsAreRunning)}
                        >
                            {measurementsAreRunning ? 'Stop' : 'Start'} Measurements
                        </Button>
                    ) : (
                        <div className="flex items-center justify-center w-full font-medium rounded-md h-9 bg-slate-300 text-slate-100">
                            {measurementsAreRunning ? 'Stop' : 'Start'} Measurements
                        </div>
                    )}
                </ModePanel>
                <ModePanel
                    label="CLI"
                    isActive={activeMode === 'cli'}
                    onClick={() => setActiveMode('cli')}
                >
                    <div>Uses a trigger from an external source.</div>
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
                </ModePanel>
            </div>
        </div>
    );
}
