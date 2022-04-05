export {};

declare global {
    interface Window {
        electron: {
            checkCliStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            playBeep: () => void;
        };
    }
}
