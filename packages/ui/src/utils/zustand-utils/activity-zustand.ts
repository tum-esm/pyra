import { create } from 'zustand';
import { z } from 'zod';
import { groupBy, sumBy } from 'lodash';

const activityHistorySchema = z.object({
    core_is_running: z.array(z.number()).length(24 * 60),
    is_measuring: z.array(z.number()).length(24 * 60),
    has_errors: z.array(z.number()).length(24 * 60),
    camtracker_startups: z.array(z.number()).length(24 * 60),
    opus_startups: z.array(z.number()).length(24 * 60),
    cli_calls: z.array(z.number()).length(24 * 60),
    upload_is_running: z.array(z.number()).length(24 * 60),
});
export type ActivityHistory = z.infer<typeof activityHistorySchema>;

export type ActivitySection = {
    from_minute_index: number;
    to_minute_index: number;
};

function parseActivityHistoryTimeSeries(ts: number[]): ActivitySection[] {
    const sections: ActivitySection[] = [];
    let currentSection: ActivitySection | undefined = undefined;
    for (let i = 0; i < ts.length; i++) {
        if (ts[i] > 0) {
            if (!currentSection) {
                currentSection = {
                    from_minute_index: i,
                    to_minute_index: i,
                };
            } else {
                currentSection.to_minute_index = i;
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
        core_is_running: ActivitySection[];
        is_measuring: ActivitySection[];
        has_errors: ActivitySection[];
        camtracker_startups: ActivitySection[];
        opus_startups: ActivitySection[];
        cli_calls: ActivitySection[];
        upload_is_running: ActivitySection[];
    };

    setActivityHistory: (ah: any) => void;
}

export const useActivityHistoryStore = create<ActivityHistoryStore>()((set) => ({
    activitySections: {
        core_is_running: [],
        is_measuring: [],
        has_errors: [],
        camtracker_startups: [],
        opus_startups: [],
        cli_calls: [],
        upload_is_running: [],
    },
    setActivityHistory: (ah: string) => {
        const parsed = activityHistorySchema.parse(ah);
        set(() => ({
            activitySections: {
                core_is_running: parseActivityHistoryTimeSeries(parsed.core_is_running),
                is_measuring: parseActivityHistoryTimeSeries(parsed.is_measuring),
                has_errors: parseActivityHistoryTimeSeries(parsed.has_errors),
                camtracker_startups: parseActivityHistoryTimeSeries(parsed.camtracker_startups),
                opus_startups: parseActivityHistoryTimeSeries(parsed.opus_startups),
                cli_calls: parseActivityHistoryTimeSeries(parsed.cli_calls),
                upload_is_running: parseActivityHistoryTimeSeries(parsed.upload_is_running),
            },
        }));
    },
}));
