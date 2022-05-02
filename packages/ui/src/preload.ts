import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    checkCLIStatus: async () => ipcRenderer.invoke('checkCLIStatus'),
    readInfoLogs: async () => ipcRenderer.invoke('readInfoLogs'),
    readDebugLogs: async () => ipcRenderer.invoke('readDebugLogs'),
    archiveLogs: async () => ipcRenderer.invoke('archiveLogs'),
    playBeep: () => ipcRenderer.invoke('playBeep'),
    readSetupJSON: async () => ipcRenderer.invoke('readSetupJSON'),
    saveSetupJSON: async (newSetupJSON: string) =>
        ipcRenderer.invoke('saveSetupJSON', newSetupJSON),
});
