export {};

declare global {
    interface Window {
        electron: {
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            clearLogs: () => void;
            playBeep: () => void;
        };
    }
}
