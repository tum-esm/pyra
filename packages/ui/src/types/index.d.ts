export {};

declare global {
    interface Window {
        electron: {
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            playBeep: () => void;
        };
    }
}
