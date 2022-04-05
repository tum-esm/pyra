declare global {
    interface Window {
        electron: {
            checkCLIStatus: () => Promise<boolean>;
            readInfoLogs: () => Promise<string>;
            readDebugLogs: () => Promise<string>;
            archiveLogs: () => void;
            playBeep: () => void;
            readSetupJSON: () => Promise<TYPES.setupJSON>;
        };
    }
}

namespace TYPES {
    export type setupJSON = {
        enclosure: {
            tum_enclosure_is_present: boolean;
        };
        em27: {
            ip: string;
        };
        plc: {
            is_present: boolean;
            ip: string;
        };
        camtracker: {
            executable_path: string;
            learn_az_elev_path: string;
            sun_intensity_path: string;
            config_path: string;
        };
        opus: {
            executable_path: string;
        };
        vbdsd: {
            sensor_is_present: boolean;
            cam_id: number;
            image_storage_path: string;
        };
    };
}

export default TYPES;
