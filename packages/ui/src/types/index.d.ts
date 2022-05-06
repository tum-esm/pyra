declare global {
    interface Window {
        electron: {
            checkCLIStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            selectPath: () => Promise<string[] | undefined>;
            playBeep: () => void;
            readSetupJSON: () => Promise<TYPES.setupJSON>;
            saveSetupJSON: (newSetupJSON: string) => Promise<string>;
        };
    }
}

namespace TYPES {
    export type configJSON = {
        [key: string]: {
            [key: string]:
                | string
                | number
                | boolean
                | {
                      [key: string]:
                          | [number, number, number]
                          | [number, number, number, number]
                          | boolean;
                  };
        };
    };
}

export default TYPES;
