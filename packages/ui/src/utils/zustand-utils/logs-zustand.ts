import { create } from 'zustand';

interface LogsStore {
    coreLogs: {
        all: string[] | undefined;
        main: string[] | undefined;
        opus: string[] | undefined;
        camtracker: string[] | undefined;
        cas: string[] | undefined;
        system_health: string[] | undefined;
        upload: string[] | undefined;
        tum_enclosure: string[] | undefined;
        helios: string[] | undefined;
    };
    uiLogs: { timestamp: number; text: string; details: string }[];
    setLogs: (allLogs: string[]) => void;
    addUiLogLine: (text: string, details: string) => void;
}

export const useLogsStore = create<LogsStore>()((set) => ({
    coreLogs: {
        all: undefined,
        main: undefined,
        opus: undefined,
        camtracker: undefined,
        cas: undefined,
        system_health: undefined,
        upload: undefined,
        tum_enclosure: undefined,
        helios: undefined,
    },
    uiLogs: [],
    setLogs: (allLogs) =>
        set(() => {
            const newLogs: {
                [key in
                    | 'all'
                    | 'main'
                    | 'opus'
                    | 'camtracker'
                    | 'cas'
                    | 'system_health'
                    | 'upload'
                    | 'tum_enclosure'
                    | 'helios']: string[];
            } = {
                all: [],
                main: [],
                opus: [],
                camtracker: [],
                cas: [],
                system_health: [],
                upload: [],
                tum_enclosure: [],
                helios: [],
            };
            let currentCategory:
                | 'main'
                | 'opus'
                | 'camtracker'
                | 'cas'
                | 'system_health'
                | 'upload'
                | 'tum_enclosure'
                | 'helios' = 'main';
            allLogs.forEach((logLine) => {
                if (logLine.trim().length > 0) {
                    // example log line: "2023-10-09 17:45:56.060208 UTC+2 - system-checks - ..."
                    if (logLine.match(/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.* - .* - .*/)) {
                        let logLineOrigin = logLine.split(' - ')[1].trim();
                        switch (logLineOrigin) {
                            case 'opus':
                                currentCategory = 'opus';
                                break;
                            case 'camtracker':
                                currentCategory = 'camtracker';
                                break;
                            case 'cas':
                                currentCategory = 'cas';
                                break;
                            case 'system-health':
                                currentCategory = 'system_health';
                                break;
                            case 'tum-enclosure':
                                currentCategory = 'tum_enclosure';
                                break;
                            case 'upload':
                                currentCategory = 'upload';
                                break;
                            case 'helios':
                                currentCategory = 'helios';
                                break;
                            default:
                                currentCategory = 'main';
                        }
                    }
                    newLogs.all.push(logLine.trim());
                    newLogs[currentCategory].push(logLine.trim());
                }
            });
            return {
                coreLogs: newLogs,
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
