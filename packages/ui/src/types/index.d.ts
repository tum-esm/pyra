declare global {
    interface Window {
        electron: {
            checkCLIStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            selectPath: () => Promise<string[] | undefined>;
            playBeep: () => void;
            readSetupJSON: () => Promise<TYPES.configJSON>;
            readParametersJSON: () => Promise<TYPES.configJSON>;
            saveSetupJSON: (newSetupJSON: TYPES.configJSON) => Promise<string>;
            saveParametersJSON: (
                newSetupJSON: TYPES.configJSON
            ) => Promise<string>;
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
                | number[]
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
