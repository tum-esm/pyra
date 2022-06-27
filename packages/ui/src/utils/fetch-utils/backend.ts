import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { customTypes } from '../../custom-types';

async function callCLI(args: string[]) {
    return await new Command(
        import.meta.env.VITE_PYTHON_VARIANT,
        [import.meta.env.VITE_PYRA_CLI_ENTRYPOINT, ...args],
        { cwd: import.meta.env.VITE_PROJECT_DIR }
    ).execute();
}

const backend = {
    readInfoLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs', 'read', '--level', 'INFO']);
    },
    readDebugLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs', 'read', '--level', 'DEBUG']);
    },
    archiveLogs: async (): Promise<ChildProcess> => {
        return await callCLI(['logs', 'archive']);
    },
    startPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'start']);
    },
    pyraCliIsAvailable: async (): Promise<ChildProcess> => {
        return await callCLI([]);
    },
    checkPyraCoreState: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'is-running']);
    },
    stopPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'stop']);
    },
    getConfig: async (): Promise<ChildProcess> => {
        return await callCLI(['config', 'get']);
    },
    updateConfig: async (newConfig: customTypes.partialConfig): Promise<ChildProcess> => {
        return await callCLI(['config', 'update', JSON.stringify(newConfig)]);
    },
    getState: async (): Promise<ChildProcess> => {
        return await callCLI(['state', 'get']);
    },
    readFromPLC: async (): Promise<ChildProcess> => {
        return await callCLI(['plc', 'read']);
    },
    writeToPLC: async (command: string[]): Promise<ChildProcess> => {
        return await callCLI(['plc', ...command]);
    },
};

export default backend;
