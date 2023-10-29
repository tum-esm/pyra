import { range } from 'lodash';
import moment from 'moment';
import {
    ActivitySection,
    useActivityHistoryStore,
    ACTIVITY_BUCKETS_PER_HOUR,
} from '../../utils/zustand-utils/activity-zustand';
import { useState } from 'react';

const SHOW_ALL_BARS: boolean = false;

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

function hourFractionToTimeString(hourFraction: number) {
    const hour = Math.floor(hourFraction);
    const minute = Math.floor((hourFraction - hour) * 60);
    return `${hour < 10 ? '0' : ''}${hour}:${minute < 10 ? '0' : ''}${minute}`;
}

function getSectionHoverLabel(
    section: ActivitySection,
    label: string,
    accumulatedValue: number,
    variant: 'fraction' | 'count'
) {
    const fraction = (accumulatedValue * ACTIVITY_BUCKETS_PER_HOUR) / 60;
    return (
        `${hourFractionToTimeString(section.from_hour)} ` +
        `- ${hourFractionToTimeString(section.to_hour)} | ${label} ` +
        (variant === 'fraction'
            ? `${Math.round(fraction * 100)} % of the time`
            : `${fraction} times`)
    );
}

function sectionToStyle(
    section: ActivitySection,
    accumulatedValue: number = 60 / ACTIVITY_BUCKETS_PER_HOUR
) {
    const opacity =
        accumulatedValue === 0
            ? 0
            : 0.25 + 0.75 * ((accumulatedValue * ACTIVITY_BUCKETS_PER_HOUR) / 60);

    return {
        left: `${(section.from_hour / 24.0) * 100}%`,
        right: `${(1 - section.to_hour / 24.0) * 100}%`,
        opacity: SHOW_ALL_BARS ? 1 : opacity,
    };
}

function ActivityPlot() {
    const now = moment();
    const { activitySections } = useActivityHistoryStore();
    const localUTCOffset = moment().utcOffset();

    const [hoverLabel, setHoverLabel] = useState<string | undefined>(undefined);

    if (activitySections === undefined) {
        return 'Loading...';
    }

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
                <div
                    className={
                        'relative flex-grow w-full h-[calc(3.5rem+2px)] border border-slate-300 rounded-lg'
                    }
                >
                    {hoverLabel !== undefined && (
                        <div className="absolute top-[-3rem] left-1/2 -translate-x-1/2 text-xs bg-slate-900 text-slate-100 rounded-md px-2 py-1 shadow-md">
                            {hoverLabel}
                        </div>
                    )}
                    {range(0.25, 24, 0.25).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0 z-10 w-[1.5px] h-14 bg-gray-600 translate-x-[-1px]"
                            style={{ left: `${h / 0.24}%` }}
                        />
                    ))}
                    {range(1, 24).map((h) => (
                        <div
                            key={h}
                            className="absolute top-0 z-10 w-[1.5px] h-14 bg-gray-400 translate-x-[-1px]"
                            style={{ left: `${h / 0.24}%` }}
                        />
                    ))}

                    {activitySections.map((s) => (
                        <>
                            <div
                                key={`core-${s.from_hour}-${s.to_hour}`}
                                className="absolute top-0 z-20 h-2 cursor-pointer bg-slate-300 hover:bg-slate-200"
                                style={sectionToStyle(s, s.isRunning)}
                                onMouseOver={() =>
                                    setHoverLabel(
                                        getSectionHoverLabel(
                                            s,
                                            'core was running',
                                            s.isRunning,
                                            'fraction'
                                        )
                                    )
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                            {s.isMeasuring > 0 && (
                                <div
                                    key={`measuring-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 bg-green-400 cursor-pointer top-2 hover:bg-green-300"
                                    style={sectionToStyle(s, s.isMeasuring)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'system was measuring',
                                                s.isMeasuring,
                                                'fraction'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                            {s.hasErrors > 0 && (
                                <div
                                    key={`error-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 bg-red-400 cursor-pointer top-4 hover:bg-red-300"
                                    style={sectionToStyle(s, s.hasErrors)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'system had errors',
                                                s.hasErrors,
                                                'fraction'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                            {s.isUploading > 0 && (
                                <div
                                    key={`uploading-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 cursor-pointer bg-fuchsia-400 top-6 hover:bg-fuchsia-300"
                                    style={sectionToStyle(s, s.isUploading)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'system was uploading',
                                                s.isUploading,
                                                'fraction'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                            {s.camtrackerStartups > 0 && (
                                <div
                                    key={`camtracker-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 cursor-pointer bg-violet-400 top-8 hover:bg-violet-300"
                                    style={sectionToStyle(s)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'camtracker was started',
                                                s.camtrackerStartups,
                                                'count'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                            {s.opusStartups > 0 && (
                                <div
                                    key={`opus-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 bg-purple-400 cursor-pointer top-10 hover:bg-purple-300"
                                    style={sectionToStyle(s)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'opus was started',
                                                s.opusStartups,
                                                'count'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                            {s.cliCalls > 0 && (
                                <div
                                    key={`camtracker-${s.from_hour}-${s.to_hour}`}
                                    className="absolute z-20 h-2 bg-indigo-400 cursor-pointer top-12 hover:bg-indigo-300"
                                    style={sectionToStyle(s)}
                                    onMouseOver={() =>
                                        setHoverLabel(
                                            getSectionHoverLabel(
                                                s,
                                                'the CLI was called',
                                                s.cliCalls,
                                                'count'
                                            )
                                        )
                                    }
                                    onMouseLeave={() => setHoverLabel(undefined)}
                                />
                            )}
                        </>
                    ))}
                    {/* blue line of current time */}
                    {/* blue label "now" */}

                    {/*<div
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
                    </div>*/}
                    {/* gray blocks of past and future time */}
                    <div
                        className="absolute top-0 z-0 h-full bg-gray-700 rounded-l-md"
                        style={{ left: 0, right: timeToPercentage(now, true) }}
                    />
                    <div
                        className="absolute top-0 z-40 h-full bg-gray-200 rounded-r-md"
                        style={{ left: timeToPercentage(now), right: 0 }}
                    />
                </div>
                <div className="relative flex flex-row items-center justify-start w-full mt-2 text-xs font-medium text-gray-700 gap-x-1">
                    <span className="px-2 py-0.5 text-slate-800 bg-slate-200 rounded-lg">
                        running
                    </span>
                    <span className="px-2 py-0.5 text-green-800 bg-green-200 rounded-lg">
                        measuring
                    </span>
                    <span className="px-2 py-0.5 text-red-800 bg-red-200 rounded-lg">error</span>
                    <span className="px-2 py-0.5 text-fuchsia-800 bg-fuchsia-200 rounded-lg">
                        uploading
                    </span>
                    <span className="px-2 py-0.5 text-purple-800 bg-purple-200 rounded-lg">
                        camtracker startups
                    </span>
                    <span className="px-2 py-0.5 text-violet-800 bg-violet-200 rounded-lg">
                        opus startups
                    </span>
                    <span className="px-2 py-0.5 text-indigo-800 bg-indigo-200 rounded-lg">
                        CLI calls
                    </span>
                    <div className="flex-grow" />
                    <div className=" text-slate-400">
                        times in UTC{localUTCOffset < 0 ? '' : '+'}
                        {localUTCOffset / 60}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ActivityPlot;
