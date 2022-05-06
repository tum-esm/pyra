import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    checkCLIStatus: async () => ipcRenderer.invoke('checkCLIStatus'),
    readInfoLogs: async () => ipcRenderer.invoke('readInfoLogs'),
    readDebugLogs: async () => ipcRenderer.invoke('readDebugLogs'),
    archiveLogs: async () => ipcRenderer.invoke('archiveLogs'),
    selectPath: async () => ipcRenderer.invoke('selectPath'),
    playBeep: () => ipcRenderer.invoke('playBeep'),
    readSetupJSON: async () => ipcRenderer.invoke('readSetupJSON'),
    readParametersJSON: async () => ipcRenderer.invoke('readParametersJSON'),
    saveSetupJSON: async (newSetupJSON: string) =>
        ipcRenderer.invoke('saveSetupJSON', newSetupJSON),
    saveParametersJSON: async (newParametersJSON: string) =>
        ipcRenderer.invoke('saveParametersJSON', newParametersJSON),
});
