import { range } from 'lodash';
import moment from 'moment';
import { functionalUtils, reduxUtils } from '../../utils';
import { customTypes } from '../../custom-types';

const borderClass = 'border border-gray-250 rounded-sm';

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

/*
type ActivitySection = { from: string; to: string };

function getActivitySectionsCore(activityHistory: customTypes.activityHistory): ActivitySection[] {
    if (activityHistory.length == 0) {
        return [{ from: '00:00:00', to: '23:59:59' }];
    } else {
        const firstEvent = activityHistory.at(0);
        let sectionList: ActivitySection[] = [];
        let currentElement: ActivitySection | undefined = {
            from: firstEvent?.event === 'start-core' ? firstEvent.localTime : '00:00:00',
            to: '23:59:59',
        };

        activityHistory.slice(1, undefined).forEach((a) => {
            if (a.event === 'start-core') {
                if (currentElement === undefined) {
                    currentElement = { from: a.localTime, to: '23:59:59' };
                }
            }
            if (a.event === 'stop-core') {
                if (currentElement !== undefined) {
                    sectionList.push({ ...currentElement, to: a.localTime });
                    currentElement = undefined;
                }
            }
        });

        if (currentElement !== undefined) {
            sectionList.push(currentElement);
        }

        return sectionList;
    }
}

function getActivitySectionsError(activityHistory: customTypes.activityHistory): ActivitySection[] {
    if (activityHistory.length == 0) {
        return [];
    } else {
        let sectionList: ActivitySection[] = [];
        let currentElement: ActivitySection | undefined = undefined;

        activityHistory.forEach((a) => {
            if (a.event === 'error-occured') {
                if (currentElement === undefined) {
                    currentElement = { from: a.localTime, to: '23:59:59' };
                }
            }
            if (a.event === 'errors-resolved') {
                if (currentElement === undefined) {
                    sectionList.push({ from: '00:00:00', to: a.localTime });
                } else {
                    sectionList.push({ from: currentElement.from, to: a.localTime });
                    currentElement = undefined;
                }
            }
        });

        if (currentElement !== undefined) {
            sectionList.push(currentElement);
        }

        return sectionList;
    }
}

function getActivitySectionsMeasurements(
    activityHistory: customTypes.activityHistory
): ActivitySection[] {
    if (activityHistory.length == 0) {
        return [];
    } else {
        let sectionList: ActivitySection[] = [];
        let currentElement: ActivitySection | undefined = undefined;

        activityHistory.forEach((a) => {
            if (a.event === 'start-measurements') {
                if (currentElement === undefined) {
                    currentElement = { from: a.localTime, to: '23:59:59' };
                }
            }
            if (a.event === 'stop-measurements') {
                if (currentElement === undefined) {
                    sectionList.push({ from: '00:00:00', to: a.localTime });
                } else {
                    sectionList.push({ from: currentElement.from, to: a.localTime });
                }
            }
            if (a.event === 'stop-core') {
                if (currentElement !== undefined) {
                    sectionList.push({ from: currentElement.from, to: a.localTime });
                }
            }
        });

        if (currentElement !== undefined) {
            sectionList.push(currentElement);
        }

        return sectionList;
    }
}


    return reduce(
        activityHistory,
        (prev: ActivitySection[], curr, index) => {
            if (curr.event === startIndicator) {
                return [...prev, { from: curr.localTime, to: '23:59:59' }];
            } else if (stopIndicators.includes(curr.event)) {
                if (startIndicator !== 'start-measurements' && prev.length == 0) {
                    return [{ from: '00:00:00', to: curr.localTime }];
                } else if (prev.length != 0) {
                    const lastFrom: any = prev.at(-1)?.from;
                    return [...prev.slice(0, -1), { from: lastFrom, to: curr.localTime }];
                } else {
                    return prev;
                }
            } else {
                return prev;
            }
        },
        []
    );
}

function getSections(
    activityHistory: customTypes.activityHistory,
    startIndicator: string,
    stopIndicators: string[]
): ActivitySection[] {
    return reduce(
        activityHistory,
        (prev: ActivitySection[], curr, index) => {
            if (curr.event === startIndicator) {
                return [...prev, { from: curr.localTime, to: '23:59:59' }];
            } else if (stopIndicators.includes(curr.event)) {
                if (startIndicator !== 'start-measurements' && prev.length == 0) {
                    return [{ from: '00:00:00', to: curr.localTime }];
                } else if (prev.length != 0) {
                    const lastFrom: any = prev.at(-1)?.from;
                    return [...prev.slice(0, -1), { from: lastFrom, to: curr.localTime }];
                } else {
                    return prev;
                }
            } else {
                return prev;
            }
        },
        []
    );
}*/

function ActivityPlot() {
    const now = moment();

    const rawActivityHistory = reduxUtils.useTypedSelector((s) => s.activity.history);

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

    const sections = functionalUtils.generateActivityHistories(activityHistory);
    console.log(sections);

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
                <div className={'relative flex-grow w-full h-5'}>
                    {sections.core.map((s) => (
                        <div
                            key={`core-${s.from}-${s.to}`}
                            className="absolute top-0 z-0 h-1 bg-blue-400 rounded-full"
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
                            className="absolute z-10 h-1 bg-green-400 rounded-full top-1.5"
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
                            className="absolute z-10 h-1 bg-red-400 rounded-full top-3"
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
                        className="absolute z-40 w-[2.5px] -mx-px bg-blue-800 -top-0.5 h-6 rounded-full"
                        style={{ left: timeToPercentage(now) }}
                    />
                    <div
                        className={
                            'absolute -top-0.5 z-40 h-6 text-blue-800 flex-row-center ' +
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
                        className="absolute top-0 z-30 h-full bg-gray-200 rounded-r-sm"
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
