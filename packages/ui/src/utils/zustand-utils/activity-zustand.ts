import { create } from 'zustand';
import { z } from 'zod';

export const MINUTES_PER_BIN = 5;

const activityHistorySchema = z.object({
    is_running: z.array(z.number()).length(24 * 60),
    is_measuring: z.array(z.number()).length(24 * 60),
    has_errors: z.array(z.number()).length(24 * 60),
    camtracker_startups: z.array(z.number()).length(24 * 60),
    opus_startups: z.array(z.number()).length(24 * 60),
    cli_calls: z.array(z.number()).length(24 * 60),
    is_uploading: z.array(z.number()).length(24 * 60),
});
export type ActivityHistory = z.infer<typeof activityHistorySchema>;

export type ActivitySection = {
    from_minute_index: number;
    to_minute_index: number;
    count: number;
};

function parseActivityHistoryTimeSeries(ts: number[]): ActivitySection[] {
    const smallerTs: number[] = [];
    for (let i = 0; i < ts.length; i++) {
        if (i % MINUTES_PER_BIN === 0) {
            smallerTs.push(ts[i]);
        } else {
            smallerTs[smallerTs.length - 1] += ts[i];
        }
    }
    const sections: ActivitySection[] = [];
    let currentSection: ActivitySection | undefined = undefined;
    for (let i = 0; i < smallerTs.length; i++) {
        if (smallerTs[i] > 0) {
            if (!currentSection) {
                currentSection = {
                    from_minute_index: i * MINUTES_PER_BIN,
                    to_minute_index: i * MINUTES_PER_BIN,
                    count: smallerTs[i],
                };
            } else {
                currentSection.to_minute_index = i * MINUTES_PER_BIN;
                currentSection.count += smallerTs[i];
            }
        } else {
            if (currentSection) {
                sections.push(currentSection);
                currentSection = undefined;
            }
        }
    }
    if (currentSection) {
        sections.push(currentSection);
    }
    return sections;
}

interface ActivityHistoryStore {
    activitySections: {
        is_running: ActivitySection[];
        is_measuring: ActivitySection[];
        has_errors: ActivitySection[];
        camtracker_startups: ActivitySection[];
        opus_startups: ActivitySection[];
        cli_calls: ActivitySection[];
        is_uploading: ActivitySection[];
    };

    setActivityHistory: (ah: any) => void;
}

export const useActivityHistoryStore = create<ActivityHistoryStore>()((set) => ({
    activitySections: {
        is_running: [],
        is_measuring: [],
        has_errors: [],
        camtracker_startups: [],
        opus_startups: [],
        cli_calls: [],
        is_uploading: [],
    },
    setActivityHistory: (ah: string) => {
        const parsed = activityHistorySchema.parse(ah);
        set(() => ({
            activitySections: {
                is_running: parseActivityHistoryTimeSeries(parsed.is_running),
                is_measuring: parseActivityHistoryTimeSeries(parsed.is_measuring),
                has_errors: parseActivityHistoryTimeSeries(parsed.has_errors),
                camtracker_startups: parseActivityHistoryTimeSeries(parsed.camtracker_startups),
                opus_startups: parseActivityHistoryTimeSeries(parsed.opus_startups),
                cli_calls: parseActivityHistoryTimeSeries(parsed.cli_calls),
                is_uploading: parseActivityHistoryTimeSeries(parsed.is_uploading),
            },
        }));
    },
}));
