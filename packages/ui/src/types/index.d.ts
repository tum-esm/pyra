export {};

declare global {
    interface Window {
        electron: {
            checkCLIStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            playBeep: () => void;
        };
    }
}
