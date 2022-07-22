import { range } from 'lodash';
import moment from 'moment';

const borderClass = 'border border-gray-200 rounded-sm';

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

function ActivityPlot() {
    const now = moment.utc();
    const then = moment.utc('09:15:00', 'hh:mm:ss');

    console.log(then.hour());

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
                        'relative flex-grow w-full h-2.5 bg-gray-350 overflow-hidden ' + borderClass
                    }
                >
                    <div
                        className="absolute top-0 z-20 h-full bg-red-200"
                        style={{ left: timeToPercentage(now), right: timeToPercentage(then, true) }}
                    />
                    <div
                        className="absolute top-0 z-10 h-full bg-green-200"
                        style={{ left: '12%', right: '30%' }}
                    />
                    <div
                        className="absolute top-0 z-0 h-full bg-white"
                        style={{ left: '10%', right: '10%' }}
                    />
                </div>
                <div className="w-full h-5 pt-1 text-xs font-medium text-gray-500 flex-row-center gap-x-4">
                    <span className="flex-row-center gap-x-1">
                        <div
                            className={
                                'flex-shrink-0 w-2.5 h-2.5 bg-gray-350 rounded-full ' + borderClass
                            }
                        />
                        core is not running
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
                        measurements running
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
