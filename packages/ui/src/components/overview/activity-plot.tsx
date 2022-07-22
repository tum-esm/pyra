import { range, reduce } from 'lodash';
import moment from 'moment';
import { reduxUtils } from '../../utils';
import { customTypes } from '../../custom-types';

const borderClass = 'border border-gray-250 rounded-sm';

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

type ActivitySection = { from: string; to: string };

function getSections(
    activityHistory: customTypes.activityHistory,
    startIndicator: string,
    stopIndicator: string
): ActivitySection[] {
    const sections = reduce(
        activityHistory,
        (prev: ActivitySection[], curr, index) => {
            if (curr.event === startIndicator) {
                return [...prev, { from: curr.time, to: '23:59:59' }];
            } else if (curr.event === stopIndicator) {
                if (prev.length == 0) {
                    return [{ from: '00:00:00', to: curr.time }];
                } else {
                    const lastFrom: any = prev.at(-1)?.from;
                    return [...prev.slice(0, -1), { from: lastFrom, to: curr.time }];
                }
            } else {
                return prev;
            }
        },
        []
    );
    return sections;
}

function ActivityPlot() {
    const now = moment.utc();

    const a = reduxUtils.useTypedSelector((s) => s.activity.history);
    console.log({ a });

    return (
        <div className="flex flex-row items-center w-full gap-x-4">
            <div className="text-sm font-semibold leading-3">Today's Activity:</div>
            <div className="flex-grow flex-col-left">
                <div className="relative grid w-full h-5 text-xs font-medium text-gray-500">
                    {range(0, 22, 3).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0 pl-1 border-l-[1.5px] border-gray-350"
                            style={{ left: `${h / 0.24}%` }}
                        >
                            {h}h{h === 0 && ' UTC'}
                        </div>
                    ))}
                </div>
                <div
                    className={
                        'relative flex-grow w-full h-4 bg-gray-300 overflow-hidden ' + borderClass
                    }
                >
                    <div
                        className="absolute top-0 z-10 h-full bg-green-200"
                        style={{ left: '12%', right: '30%' }}
                    />
                    {/* blue line of current time */}
                    <div
                        className="absolute top-0 z-0 h-full bg-white"
                        style={{ left: '10%', right: '10%' }}
                    />
                    {/* blue label "now" */}
                    <div
                        className="absolute z-40 w-[2px] -mx-px bg-blue-500 top-0 h-full"
                        style={{ left: timeToPercentage(now) }}
                    />
                    <div
                        className={
                            'absolute top-0 z-40 h-full text-blue-500 flex-row-center ' +
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
                        className="absolute top-0 z-30 h-full bg-gray-150"
                        style={{ left: timeToPercentage(now), right: 0 }}
                    />
                </div>
                <div className="w-full h-5 pt-1 text-xs font-medium text-gray-500 flex-row-center gap-x-4">
                    <span className="flex-row-center gap-x-1">
                        <div
                            className={
                                'flex-shrink-0 w-2.5 h-2.5 bg-gray-300 rounded-full ' + borderClass
                            }
                        />
                        core not running
                    </span>
                    <span className="flex-row-center gap-x-1">
                        <div
                            className={
                                'flex-shrink-0 w-2.5 h-2.5 bg-white rounded-full ' + borderClass
                            }
                        />
                        idle
                    </span>
                    <span className="flex-row-center gap-x-1">
                        <div
                            className={
                                'flex-shrink-0 w-2.5 h-2.5 bg-green-200 rounded-full ' + borderClass
                            }
                        />
                        measuring
                    </span>
                    <span className="flex-row-center gap-x-1">
                        <div
                            className={
                                'flex-shrink-0 w-2.5 h-2.5 bg-red-200 rounded-full ' + borderClass
                            }
                        />
                        error occured
                    </span>
                </div>
            </div>
        </div>
    );
}

export default ActivityPlot;
