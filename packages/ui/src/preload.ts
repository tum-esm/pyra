import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    readInfoLogs: async () => ipcRenderer.invoke('readInfoLogs'),
    readDebugLogs: async () => ipcRenderer.invoke('readDebugLogs'),
    playBeep: () => ipcRenderer.invoke('playBeep'),
});
