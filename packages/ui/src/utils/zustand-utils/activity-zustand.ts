import { create } from 'zustand';

export type ActivityHistory = {
    localTime: string;
    event:
        | 'start-core'
        | 'stop-core'
        | 'start-measurements'
        | 'stop-measurements'
        | 'error-occured'
        | 'errors-resolved';
}[];

interface ActivityState {
    activityHistory: ActivityHistory | undefined;
    setActivityHistory: (ah: ActivityHistory) => void;
}

export const useActivityHistoryStore = create<ActivityState>()((set) => ({
    activityHistory: undefined,
    setActivityHistory: (ah) => set(() => ({ activityHistory: ah })),
}));
