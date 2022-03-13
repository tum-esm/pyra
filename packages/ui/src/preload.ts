import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    showDialog: async () => ipcRenderer.invoke('dialog:open'),
});
