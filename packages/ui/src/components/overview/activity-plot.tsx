import { range } from 'lodash';
import moment from 'moment';
import { functionalUtils, reduxUtils } from '../../utils';
import { customTypes } from '../../custom-types';

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

    const rawActivityHistory = reduxUtils.useTypedSelector((s) => s.activity.history);
    const currentInfoLogLines = reduxUtils.useTypedSelector((s) => s.logs.infoLines);

    let measurementsAreRunning = false;
    let errorIsPresent = false;
    if (currentInfoLogLines !== undefined) {
        const joined_logs = functionalUtils
            .reduceLogLines(currentInfoLogLines, '3 iterations')
            .join('\n');
        measurementsAreRunning =
            joined_logs.includes(' - INFO - Measurements should be running is set to: True') &&
            !joined_logs.includes(' - INFO - Measurements should be running is set to: False');
        errorIsPresent =
            joined_logs.includes(' - EXCEPTION - ') &&
            !joined_logs.includes(' - ERROR - Invalid config, waiting 10 seconds');
    }

    let activityHistory: customTypes.activityHistory = [];
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
                <div className="relative grid w-full h-5 text-xs font-medium text-gray-400">
                    {range(0, 23, 2).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0  before:w-0.5 before:bg-gray-300 before:h-4 before:absolute before:mr-2 before:rounded-full"
                            style={{ left: `${h / 0.24}%` }}
                        >
                            <span className="pl-1">
                                {h !== 0 && h}
                                {h === 0 &&
                                    `${h}h UTC` +
                                        (localUTCOffset < 0 ? '' : '+') +
                                        (localUTCOffset / 60).toString()}
                            </span>
                        </div>
                    ))}
                </div>
                <div className={'relative flex-grow w-full h-6'}>
                    {sections.core.map((s) => (
                        <div
                            key={`core-${s.from}-${s.to}`}
                            className="absolute z-10 h-1 bg-blue-400 rounded-full top-1"
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
                            className="absolute z-10 h-1 bg-green-400 rounded-full top-2.5"
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
                            className="absolute z-10 h-1 bg-red-400 rounded-full top-4"
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
                        className="absolute z-30 w-[2.5px] -mx-px bg-gray-900 -top-0.5 h-7 rounded-full"
                        style={{ left: timeToPercentage(now) }}
                    />
                    <div
                        className={
                            'absolute -top-0.5 z-30 h-7 text-gray-900 flex-row-center ' +
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
                    {/* gray block of future time */}
                    <div
                        className="absolute top-0 z-0 h-full bg-gray-700 rounded-l"
                        style={{ left: 0, right: timeToPercentage(now, true) }}
                    />
                    <div
                        className="absolute top-0 z-20 h-full bg-gray-300 rounded-r"
                        style={{ left: timeToPercentage(now), right: 0 }}
                    />
                </div>
                <div className="w-full h-5 pt-1 text-xs font-medium text-gray-500 flex-row-center gap-x-4">
                    <span className="flex-row-center gap-x-1">
                        <div className={'flex-shrink-0 w-2.5 h-2.5 bg-blue-400 rounded-sm '} />
                        core is running
                    </span>
                    <span className="flex-row-center gap-x-1">
                        <div className={'flex-shrink-0 w-2.5 h-2.5 bg-green-400 rounded-sm '} />
                        measuring
                    </span>
                    <span className="flex-row-center gap-x-1">
                        <div className={'flex-shrink-0 w-2.5 h-2.5 bg-red-400 rounded-sm '} />
                        error occured
                    </span>
                </div>
            </div>
        </div>
    );
}

export default ActivityPlot;
