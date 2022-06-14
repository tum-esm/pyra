import backend from '../../utils/backend';
import { useState, useEffect } from 'react';
import TYPES from '../../utils/types';

function Table(props: { children: React.ReactNode }) {
    return (
        <div className="w-full">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                    <tbody className="bg-white divide-y divide-gray-200">
                        {props.children}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function renderProperty(p: any, connection: boolean = false) {
    if (p === null) {
        return <span className="text-gray-500">-</span>;
    }
    if (p === true) {
        return (
            <span className="text-green-600">
                {connection ? 'is connected' : 'Yes'}
            </span>
        );
    }
    if (p === false) {
        return (
            <span className="text-red-600">
                {connection ? 'is not connected' : 'No'}
            </span>
        );
    }
    return <span className="text-blue-600">{p}</span>;
}

function TableRow(props: { label: string; value: React.ReactNode }) {
    return (
        <tr>
            <td className="py-2 pl-4 text-sm font-medium text-gray-900 whitespace-nowrap">
                {props.label}
            </td>
            <td className="w-20 px-4 py-2 text-sm font-medium text-left whitespace-nowrap">
                {props.value}
            </td>
        </tr>
    );
}
export default function PyraCoreState(props: {}) {
    const [stateJSON, setStateJSON] = useState<TYPES.state | undefined>(undefined);
    const [loading, setLoading] = useState(false);

    async function loadStateJSON() {
        setLoading(true);
        const p = await backend.getState();
        try {
            setStateJSON(JSON.parse(p.stdout));
        } catch {
            setStateJSON(undefined);
        }
        setLoading(false);
    }

    useEffect(() => {
        loadStateJSON();
    }, []);

    const pss = [
        [
            {
                key: 'PLC',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.state.computer,
                    true
                ),
            },
            {
                key: 'Camera',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.state.camera,
                    true
                ),
            },
            {
                key: 'Router',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.state.router,
                    true
                ),
            },
            {
                key: 'EM27',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.state.spectrometer,
                    true
                ),
            },
        ],
        [
            {
                key: 'Fan Speed',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.actors.fan_speed
                ),
            },
            {
                key: 'Current Angle',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.actors.current_angle
                ),
            },
            {
                key: 'Humidity',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.sensors.humidity
                ),
            },
            {
                key: 'Temperature',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.sensors.temperature
                ),
            },
        ],
        [
            {
                key: 'Rain',
                value: renderProperty(stateJSON?.enclosure_plc_readings.state.rain),
            },
            {
                key: 'Cover Closed',
                value: renderProperty(
                    stateJSON?.enclosure_plc_readings.state.cover_closed
                ),
            },
        ],
    ];

    return (
        <div className={'w-full text-sm flex-row-left gap-x-2 px-6'}>
            {loading && '...'}
            {!loading &&
                stateJSON === undefined &&
                'state of pyra-core could not be loaded'}
            {!loading && stateJSON !== undefined && (
                <div className="grid w-full grid-cols-3 gap-x-4">
                    {pss.map((ps) => (
                        <Table>
                            {ps.map((p) => (
                                <TableRow key={p.key} label={p.key} value={p.value} />
                            ))}
                        </Table>
                    ))}
                </div>
            )}
        </div>
    );
}
