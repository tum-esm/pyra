import { range } from 'lodash';
import moment from 'moment';
import {
    MINUTES_PER_BIN,
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
        right: `${(1 - (section.to_minute_index + MINUTES_PER_BIN) / (24 * 60)) * 100}%`,
    };
}

function getSectionHoverLabel(
    label: string,
    section: ActivitySection,
    variant: 'count' | 'span' = 'span'
) {
    const pad = (n: number) => n.toString().padStart(2, '0');
    const tts = (n: number) => `${pad(Math.floor(n / 60))}:${pad(n % 60)}`;

    if (variant === 'count') {
        return `${label}  ${section.count} time${section.count != 1 ? 's' : ''} between ${tts(
            section.from_minute_index
        )} to ${tts(section.to_minute_index + MINUTES_PER_BIN)}`;
    } else {
        return `${label} from ${tts(section.from_minute_index)} to ${tts(
            section.to_minute_index + MINUTES_PER_BIN
        )}`;
    }
}

function ActivityPlot() {
    const { activitySections } = useActivityHistoryStore();
    const localUTCOffset = moment().utcOffset();
    const [hoverLabel, setHoverLabel] = useState<string | undefined>(undefined);

    const now = moment();

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
                <div className={'relative flex-grow w-full h-[calc(3rem+2px)]'}>
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
                        {range(1 / 6, 24, 1 / 6).map((h) => (
                            <div
                                key={`thin-hour-line-${h}`}
                                className="absolute top-0 z-10 w-[1px] h-12 bg-gray-600 translate-x-[-1px]"
                                style={{ left: `${h / 0.24}%` }}
                            />
                        ))}
                        {range(1, 24).map((h) => (
                            <div
                                key={`bold-hour-line-${h}`}
                                className="absolute top-0 z-10 w-[1px] h-12 bg-gray-400 translate-x-[-1px]"
                                style={{ left: `${h / 0.24}%` }}
                            />
                        ))}
                        {activitySections.is_running.map((s) => (
                            <div
                                className="absolute top-0 z-20 h-2 cursor-pointer bg-slate-300 hover:bg-slate-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('core was running', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.is_measuring.map((s) => (
                            <div
                                className="absolute z-20 h-2 bg-green-300 cursor-pointer top-2 hover:bg-green-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('was measuring', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.has_errors.map((s) => (
                            <div
                                className="absolute z-20 h-2 bg-red-300 cursor-pointer top-4 hover:bg-red-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('core had errors', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.is_uploading.map((s) => (
                            <div
                                className="absolute z-20 h-2 cursor-pointer bg-fuchsia-300 top-6 hover:bg-fuchsia-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(getSectionHoverLabel('was uploading', s))
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.camtracker_startups.map((s) => (
                            <div
                                className="absolute z-20 h-2 cursor-pointer bg-violet-300 top-8 hover:bg-violet-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(
                                        getSectionHoverLabel('camtracker was started', s, 'count')
                                    )
                                }
                                onMouseLeave={() => setHoverLabel(undefined)}
                            />
                        ))}
                        {activitySections.opus_startups.map((s) => (
                            <div
                                className="absolute z-20 h-2 bg-purple-300 cursor-pointer top-10 hover:bg-purple-200"
                                style={sectionToStyle(s)}
                                onMouseOver={() =>
                                    setHoverLabel(
                                        getSectionHoverLabel('opus was started', s, 'count')
                                    )
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
