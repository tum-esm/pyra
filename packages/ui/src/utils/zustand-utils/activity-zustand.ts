import { create } from 'zustand';
import { z } from 'zod';
import { groupBy, sumBy } from 'lodash';

export const ACTIVITY_BUCKETS_PER_HOUR = 4;

const activityHistorySchema = z.array(
    z
        .object({
            local_time: z.string(),
            is_measuring: z.boolean(),
            has_errors: z.boolean(),
            is_uploading: z.boolean(),
            camtracker_startups: z.number(),
            opus_startups: z.number(),
            cli_calls: z.number(),
        })
        .transform((data) => ({
            localTime: data.local_time,
            isMeasuring: data.is_measuring,
            hasErrors: data.has_errors,
            isUploading: data.is_uploading,
            camtrackerStartups: data.camtracker_startups,
            opusStartups: data.opus_startups,
            cliCalls: data.cli_calls,
        }))
);

export type ActivityHistory = z.infer<typeof activityHistorySchema>;

export type ActivitySection = {
    from_hour: number;
    to_hour: number;
    isRunning: number;
    isMeasuring: number;
    hasErrors: number;
    isUploading: number;
    camtrackerStartups: number;
    opusStartups: number;
    cliCalls: number;
};

function parseActivityHistory(activityHistory: ActivityHistory): ActivitySection[] {
    const groupedBySection = groupBy(activityHistory, (ah) => {
        const hour = parseInt(ah.localTime.split(':')[0]);
        const minute = parseInt(ah.localTime.split(':')[1]);
        return (
            hour + Math.floor((minute / 60) * ACTIVITY_BUCKETS_PER_HOUR) / ACTIVITY_BUCKETS_PER_HOUR
        );
    });
    return Object.entries(groupedBySection).map(([key, value]) => ({
        from_hour: parseFloat(key),
        to_hour: parseFloat(key) + 1 / ACTIVITY_BUCKETS_PER_HOUR,
        isRunning: value.length,
        isMeasuring: sumBy(value, 'isMeasuring'),
        hasErrors: sumBy(value, 'hasErrors'),
        isUploading: sumBy(value, 'isUploading'),
        camtrackerStartups: sumBy(value, 'camtrackerStartups'),
        opusStartups: sumBy(value, 'opusStartups'),
        cliCalls: sumBy(value, 'cliCalls'),
    }));
}

interface ActivityHistoryStore {
    activitySections: ActivitySection[] | undefined;
    setActivityHistory: (ah: any) => void;
}

export const useActivityHistoryStore = create<ActivityHistoryStore>()((set) => ({
    activitySections: undefined,
    setActivityHistory: (ah: any) =>
        set(() => ({ activitySections: parseActivityHistory(activityHistorySchema.parse(ah)) })),
}));
