import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    checkCliStatus: async () => ipcRenderer.invoke('checkCliStatus'),
    readInfoLogs: async () => ipcRenderer.invoke('readInfoLogs'),
    readDebugLogs: async () => ipcRenderer.invoke('readDebugLogs'),
    archiveLogs: async () => ipcRenderer.invoke('archiveLogs'),
    playBeep: () => ipcRenderer.invoke('playBeep'),
});
