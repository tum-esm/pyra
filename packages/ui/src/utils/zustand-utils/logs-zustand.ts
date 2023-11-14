import { create } from 'zustand';

interface LogsStore {
    allLogs: string[] | undefined;
    mainLogs: string[] | undefined;
    uploadLogs: string[] | undefined;
    heliosLogs: string[] | undefined;
    uiLogs: { timestamp: number; text: string; details: string }[];
    setLogs: (allLogs: string[]) => void;
    addUiLogLine: (text: string, details: string) => void;
}

export const useLogsStore = create<LogsStore>()((set) => ({
    allLogs: undefined,
    mainLogs: undefined,
    uploadLogs: undefined,
    heliosLogs: undefined,
    uiLogs: [],
    setLogs: (allLogs) =>
        set(() => {
            const newLogs: {
                [key in 'main' | 'upload' | 'helios']: string[];
            } = {
                main: [],
                upload: [],
                helios: [],
            };
            let currentCategory: 'main' | 'upload' | 'helios' = 'main';
            allLogs.forEach((logLine) => {
                if (logLine.replace(' ', '').length > 0) {
                    // example log line:
                    // 2023-10-09 17:45:56.060208 UTC+2 - system-checks -
                    if (logLine.match(/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.* - .* - .*/)) {
                        if (logLine.split(' - ')[1].trim() === 'upload') {
                            currentCategory = 'upload';
                        } else if (logLine.split(' - ')[1].trim() === 'helios') {
                            currentCategory = 'helios';
                        } else {
                            currentCategory = 'main';
                        }
                    }
                    newLogs[currentCategory].push(logLine);
                }
            });
            return {
                allLogs,
                mainLogs: newLogs.main,
                uploadLogs: newLogs.upload,
                heliosLogs: newLogs.helios,
            };
        }),
    addUiLogLine: (text, details) =>
        set((state) => ({
            uiLogs: [
                ...state.uiLogs.filter((logLine) => logLine.timestamp > Date.now() - 600000), // 10 minutes
                {
                    timestamp: Date.now(),
                    text,
                    details,
                },
            ],
        })),
}));
