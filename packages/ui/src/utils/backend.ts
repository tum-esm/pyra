import { Command, ChildProcess } from '@tauri-apps/api/shell';
import TYPES from './types';

async function callCLI(args: string[]) {
    return await new Command('pyra-cli', [
        "packages\\cli\\main.py",
       ...args
    ],{cwd: "C:\\pyra-4"}).execute();
}

const backend = {
    readInfoLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs','read','--level','INFO']);
    },
    readDebugLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs','read','--level','DEBUG']);
    },
    archiveLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs','archive']);
    },
    startPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core','start']);
    },
    pyraCliIsAvailable: async (): Promise<boolean> => {
        const p = await callCLI([]);
        return p.stdout.includes('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...');
    },
    checkPyraCoreState: async (): Promise<ChildProcess> => {
        return await callCLI(['core','is-running']);
    },
    stopPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core','stop']);
    },
    getConfig: async (): Promise<ChildProcess> => {
        return await callCLI(['config','get']);
    },
    updateConfig: async (newConfig: TYPES.partialConfig): Promise<ChildProcess> => {
        return await callCLI(['config','update',  JSON.stringify(newConfig)]);
    },
    getState: async (): Promise<ChildProcess> => {
        return await callCLI(['state','get']);
    },
};

export default backend;
