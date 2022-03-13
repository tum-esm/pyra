export {};

declare global {
    interface Window {
        electron: {
            readInfoLogs: () => Promise<string>;
        };
    }
}
