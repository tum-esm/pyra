import { range } from 'lodash';
import moment from 'moment';
import { functionalUtils } from '../../utils';
import { useLogsStore } from '../../utils/zustand-utils/logs-zustand';
import {
    ActivityHistory,
    useActivityHistoryStore,
} from '../../utils/zustand-utils/activity-zustand';

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

function ActivityPlot() {
    const now = moment();

    // " - INFO - Measurements should be running is set to: true"
    // " - EXCEPTION - "

    const { activityHistory: rawActivityHistory } = useActivityHistoryStore();
    const { mainLogs } = useLogsStore();

    let measurementsAreRunning = false;
    let errorIsPresent = false;
    if (mainLogs !== undefined) {
        let mainloopIterationLogs = mainLogs.join('\n').split('main - INFO - Starting iteration');
        if (mainloopIterationLogs.length > 2) {
            mainloopIterationLogs = mainloopIterationLogs.slice(0, 2);
        }
        const joinedLogs = mainloopIterationLogs.join('main - INFO - Starting iteration');
        measurementsAreRunning =
            joinedLogs.includes(' - INFO - Measurements should be running is set to: True') &&
            !joinedLogs.includes(' - INFO - Measurements should be running is set to: False');
        errorIsPresent =
            joinedLogs.includes(' - EXCEPTION - ') &&
            !joinedLogs.includes(' - ERROR - Invalid config, waiting 10 seconds');
    }

    let activityHistory: ActivityHistory = [];
    if (rawActivityHistory !== undefined) {
        if (rawActivityHistory.length === 0 || rawActivityHistory.at(0)?.event !== 'start-core') {
            activityHistory = [
                { event: 'start-core', localTime: '00:00:00' },
                ...rawActivityHistory,
            ];
        } else {
            activityHistory = rawActivityHistory;
        }
    }

    const sections = functionalUtils.generateActivityHistories(
        activityHistory,
        measurementsAreRunning,
        errorIsPresent
    );
    const localUTCOffset = moment().utcOffset();

    return (
        <div className="flex flex-row items-center w-full gap-x-4">
            <div className="flex-grow flex-col-left">
                <div className="relative grid w-full h-4 text-[0.6rem] font-medium text-gray-400">
                    {range(2, 23, 2).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0 -translate-x-1/2"
                            style={{ left: `${h / 0.24}%` }}
                        >
                            {h}
                        </div>
                    ))}
                </div>
                <div className={'relative flex-grow w-full h-9'}>
                    {range(1, 24).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0 z-10 w-[1.5px] h-6 bg-gray-500 translate-x-[-1px]"
                            style={{ left: `${h / 0.24}%` }}
                        />
                    ))}
                    {sections.core.map((s) => (
                        <div
                            key={`core-${s.from}-${s.to}`}
                            className="absolute z-20 h-2 bg-blue-400 rounded-sm top-1"
                            style={{
                                left: timeToPercentage(moment(s.from, 'HH:mm:ss', true)),
                                right: timeToPercentage(moment(s.to, 'HH:mm:ss', true), true),
                                minWidth: '0.25rem',
                            }}
                        />
                    ))}
                    {sections.measurements.map((s) => (
                        <div
                            key={`measurements-${s.from}-${s.to}`}
                            className="absolute z-20 h-2 bg-green-400 rounded-sm top-3.5"
                            style={{
                                left: timeToPercentage(moment(s.from, 'HH:mm:ss', true)),
                                right: timeToPercentage(moment(s.to, 'HH:mm:ss', true), true),
                                minWidth: '0.25rem',
                            }}
                        />
                    ))}
                    {sections.error.map((s) => (
                        <div
                            key={`error-${s.from}-${s.to}`}
                            className="absolute z-20 h-2 bg-red-400 rounded-sm top-6"
                            style={{
                                left: timeToPercentage(moment(s.from, 'HH:mm:ss', true)),
                                right: timeToPercentage(moment(s.to, 'HH:mm:ss', true), true),
                                minWidth: '0.25rem',
                            }}
                        />
                    ))}
                    {/* blue line of current time */}
                    {/* blue label "now" */}

                    <div
                        className="absolute z-30 w-[2.5px] -mx-px bg-gray-900 -top-0.5 h-10 rounded-full"
                        style={{ left: timeToPercentage(now) }}
                    />
                    <div
                        className={
                            'absolute -top-0.5 z-30 h-10 text-gray-900 flex-row-center ' +
                            'px-1 text-xs font-medium'
                        }
                        style={
                            now.hour() < 23
                                ? { left: timeToPercentage(now) }
                                : { right: timeToPercentage(now, true) }
                        }
                    >
                        now
                    </div>
                    {/* gray blocks of past and future time */}
                    <div
                        className="absolute top-0 z-0 h-full bg-gray-700 rounded-l"
                        style={{ left: -2, right: timeToPercentage(now, true) }}
                    />
                    <div
                        className="absolute top-0 z-20 h-full bg-gray-200 rounded-r"
                        style={{ left: timeToPercentage(now), right: -2 }}
                    />
                </div>
                <div className="relative flex flex-row items-center justify-start w-full mt-2 text-xs font-medium text-gray-700 gap-x-1">
                    <span className="px-2 py-0.5 text-blue-800 bg-blue-200 rounded-lg">
                        running
                    </span>
                    <span className="px-2 py-0.5 text-green-800 bg-green-200 rounded-lg">
                        measuring
                    </span>
                    <span className="px-2 py-0.5 text-red-800 bg-red-200 rounded-lg">error</span>
                    <div className="absolute right-0 text-slate-400">
                        times in UTC{localUTCOffset < 0 ? '' : '+'}
                        {localUTCOffset / 60}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ActivityPlot;
