/**
 * Returned from the Electron Dialog API `showOpenDialog`
 * @see: https://www.electronjs.org/docs/latest/api/dialog
 */
export type DialogFileData = {
    /**
     * Did user cancel dialog?
     */
    cancelled: boolean;
    /**
     * Array of file paths that user selected
     */
    filePaths: string[];
};

declare global {
    interface Window {
        electron: {
            showDialog: () => Promise<DialogFileData>;
        };
    }
}
