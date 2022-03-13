export {};

declare global {
    interface Window {
        electron: {
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            playBeep: () => void;
        };
    }
}
