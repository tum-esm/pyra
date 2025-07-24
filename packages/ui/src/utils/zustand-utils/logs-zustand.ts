import { create } from 'zustand';

interface LogsStore {
    coreLogs: {
        all: string[] | undefined;
        main: string[] | undefined;
        opus: string[] | undefined;
        camtracker: string[] | undefined;
        cas: string[] | undefined;
        system_monitor: string[] | undefined;
        upload: string[] | undefined;
        tum_enclosure: string[] | undefined;
        coccon_spain_enclosure: string[] | undefined;
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
        system_monitor: undefined,
        upload: undefined,
        tum_enclosure: undefined,
        coccon_spain_enclosure: undefined,
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
                    | 'system_monitor'
                    | 'upload'
                    | 'tum_enclosure'
                    | 'coccon_spain_enclosure'
                    | 'helios']: string[];
            } = {
                all: [],
                main: [],
                opus: [],
                camtracker: [],
                cas: [],
                system_monitor: [],
                upload: [],
                tum_enclosure: [],
                coccon_spain_enclosure: [],
                helios: [],
            };
            let currentCategory:
                | 'main'
                | 'opus'
                | 'camtracker'
                | 'cas'
                | 'system_monitor'
                | 'upload'
                | 'tum_enclosure'
                | 'coccon_spain_enclosure'
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
                            case 'system-monitor':
                                currentCategory = 'system_monitor';
                                break;
                            case 'tum-enclosure':
                                currentCategory = 'tum_enclosure';
                                break;
                            case 'coccon-spain-enclosure':
                                currentCategory = 'coccon_spain_enclosure';
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
