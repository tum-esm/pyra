import { range } from 'lodash';
import moment from 'moment';
import {
    ActivitySection,
    useActivityHistoryStore,
    ACTIVITY_BUCKETS_PER_HOUR,
} from '../../utils/zustand-utils/activity-zustand';
import { useState } from 'react';
import React from 'react';

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
            : `${accumulatedValue} times`)
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
        return <div>loading ...</div>;
    }

    return (
        <div className="flex flex-row items-center w-full gap-x-4">
            <div className="flex-grow flex-col-left">
                <div className="relative grid w-full h-4 text-[0.6rem] font-medium text-gray-400">
                    {range(2, 23, 2).map((h) => (
                        <div
                            key={`hour-label-${h}`}
                            className="absolute top-0 p-px -translate-x-1/2"
                            style={{ left: `${h / 0.24}%` }}
                        >
                            {h}
                        </div>
                    ))}
                </div>
                <div className={'relative flex-grow w-full h-[calc(3.5rem+2px)]'}>
                    {hoverLabel !== undefined && (
                        <div className="absolute top-[-2.75rem] px-2 py-1 text-xs -translate-x-1/2 rounded-md shadow-md left-1/2 bg-slate-900 text-slate-100">
                            {hoverLabel}
                        </div>
                    )}
                    <div
                        className={
                            'w-full relative h-full border border-slate-200 rounded-lg overflow-hidden'
                        }
                    >
                        {range(0.25, 24, 0.25).map((h) => (
                            <div
                                key={`thin-hour-line-${h}`}
                                className="absolute top-0 z-10 w-[1.5px] h-14 bg-gray-600 translate-x-[-1px]"
                                style={{ left: `${h / 0.24}%` }}
                            />
                        ))}
                        {range(1, 24).map((h) => (
                            <div
                                key={`bold-hour-line-${h}`}
                                className="absolute top-0 z-10 w-[1.5px] h-14 bg-gray-400 translate-x-[-1px]"
                                style={{ left: `${h / 0.24}%` }}
                            />
                        ))}
                        {activitySections.map((s, i) => (
                            <React.Fragment key={i}>
                                <div
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
                            </React.Fragment>
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
                            className="absolute top-0 z-0 h-full bg-gray-700 rounded-l-lg"
                            style={{ left: 0, right: timeToPercentage(now, true) }}
                        />
                        <div
                            className="absolute top-0 z-40 h-full bg-gray-100 rounded-r-lg"
                            style={{ left: timeToPercentage(now), right: 0 }}
                        />
                    </div>
                </div>
                <div className="relative flex flex-row items-center justify-start w-full mt-0 overflow-hidden text-xs font-medium text-gray-700">
                    <div className="relative flex flex-row items-center justify-start h-6 mt-2 overflow-hidden text-xs font-medium leading-6 text-gray-700 border divide-x rounded-lg gap-x-0 divide-slate-300 border-slate-300">
                        <span className="px-2 py-0.5 text-slate-700 bg-slate-100">running</span>
                        <span className="px-2 py-0.5 text-green-700 bg-green-100">measuring</span>
                        <span className="px-2 py-0.5 text-red-700 bg-red-100">error</span>
                        <span className="px-2 py-0.5 text-fuchsia-700 bg-fuchsia-100">
                            uploading
                        </span>
                        <span className="px-2 py-0.5 text-purple-700 bg-purple-100">
                            camtracker startups
                        </span>
                        <span className="px-2 py-0.5 text-violet-700 bg-violet-100">
                            opus startups
                        </span>
                        <span className="px-2 py-0.5 text-indigo-700 bg-indigo-100">CLI calls</span>
                    </div>
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
