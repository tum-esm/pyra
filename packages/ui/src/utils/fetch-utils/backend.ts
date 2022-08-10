import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { customTypes } from '../../custom-types';
import { join } from '@tauri-apps/api/path';
import fetchUtils from '.';

async function callCLI(args: string[]) {
    let projectDirPath = await fetchUtils.getProjectDirPath();

    let pythonInterpreter =
        import.meta.env.VITE_ENVIRONMENT === 'development-moritz' ? 'venv-python' : 'system-python';
    let pyraCLIEntrypoint = await join('packages', 'cli', 'main.py');

    const commandString = [pythonInterpreter, pyraCLIEntrypoint, ...args].join(' ');
    console.debug(`Running shell command: "${commandString}" in directory "${projectDirPath}"`);

    return await new Command(pythonInterpreter, [pyraCLIEntrypoint, ...args], {
        cwd: projectDirPath,
    }).execute();
}

const backend = {
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
    writeToPLC: async (command: string[]): Promise<ChildProcess> => {
        return await callCLI(['plc', ...command]);
    },
};

export default backend;
