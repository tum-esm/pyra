import { range } from 'lodash';
import moment from 'moment';
import {
    ActivitySection,
    useActivityHistoryStore,
} from '../../utils/zustand-utils/activity-zustand';
import { useState } from 'react';

function timeToPercentage(time: moment.Moment, fromRight: boolean = false) {
    let fraction = time.hour() / 24.0 + time.minute() / (24.0 * 60) + time.second() / (24.0 * 3600);
    if (fromRight) {
        fraction = 1 - fraction;
    }
    return `${(fraction * 100).toFixed(2)}%`;
}

function sectionToStyle(section: ActivitySection) {
    return {
        left: `${(section.from_minute_index / (24 * 60)) * 100}%`,
        right: `${(1 - (section.to_minute_index + 1) / (24 * 60)) * 100}%`,
    };
}

function getSectionHoverLabel(label: string, section: ActivitySection) {
    const fromTime = `${Math.floor(section.from_minute_index / 60)}:${
        section.from_minute_index % 60
    }`;
    const toTime = `${Math.floor((section.to_minute_index + 1) / 60)}:${
        (section.to_minute_index + 1) % 60
    }`;
    return `${label} from ${fromTime} to ${toTime}`;
}

function ActivityPlot() {
    const { activitySections } = useActivityHistoryStore();
    const localUTCOffset = moment().utcOffset();
    const [hoverLabel, setHoverLabel] = useState<string | undefined>(undefined);

    const now = moment();

    if (activitySections === undefined) {
        return <div>loading ...</div>;
    }

    // TODO: reintroduce the counted hover labels

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
                        {activitySections.is_running.map((s, i) => (
                            <div
                                className="absolute top-0 z-20 h-2 cursor-pointer bg-slate-300 hover:bg-slate-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('core was running', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.is_measuring.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 bg-green-300 cursor-pointer top-2 hover:bg-green-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('was measuring', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.has_errors.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 bg-red-300 cursor-pointer top-4 hover:bg-red-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('core had errors', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.is_uploading.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 cursor-pointer bg-fuchsia-300 top-6 hover:bg-fuchsia-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('was uploading', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.camtracker_startups.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 cursor-pointer bg-violet-300 top-8 hover:bg-violet-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('camtracker was started', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.opus_startups.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 bg-purple-300 cursor-pointer top-10 hover:bg-purple-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('opus was started', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.cli_calls.map((s, i) => (
                            <div
                                className="absolute z-20 h-2 bg-indigo-300 cursor-pointer top-12 hover:bg-indigo-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('CLI was called', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}

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
