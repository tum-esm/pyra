import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { customTypes } from '../../custom-types';
import { join } from '@tauri-apps/api/path';
import fetchUtils from '.';
import { Config } from '../zustand-utils/config-zustand';

async function callCLI(args: string[]): Promise<ChildProcess> {
    let projectDirPath = await fetchUtils.getProjectDirPath();

    let pythonInterpreter =
        import.meta.env.VITE_ENVIRONMENT === 'development-moritz' ? 'venv-python' : 'system-python';
    let pyraCLIEntrypoint = await join('packages', 'cli', 'main.py');

    const commandString = [pythonInterpreter, pyraCLIEntrypoint, ...args].join(' ');
    console.debug(`Running shell command: "${commandString}" in directory "${projectDirPath}"`);

    return new Promise(async (resolve, reject) => {
        const result = await new Command(pythonInterpreter, [pyraCLIEntrypoint, ...args], {
            cwd: projectDirPath,
        }).execute();
        if (result.code === 0) {
            resolve(result);
        } else {
            reject(result);
        }
    });
}

const backend = {
    pyraCliIsAvailable: async (): Promise<ChildProcess> => {
        return await callCLI([]);
    },
    checkPyraCoreState: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'is-running']);
    },
    startPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'start']);
    },
    stopPyraCore: async (): Promise<ChildProcess> => {
        return await callCLI(['core', 'stop']);
    },
    getConfig: async (): Promise<ChildProcess> => {
        return await callCLI(['config', 'get', '--no-indent', '--no-color']);
    },
    updateConfig: async (newConfig: any): Promise<ChildProcess> => {
        return await callCLI(['config', 'update', JSON.stringify(newConfig)]);
    },
    writeToPLC: async (command: string[]): Promise<ChildProcess> => {
        return await callCLI(['plc', ...command]);
    },
    testEmail: async (): Promise<ChildProcess> => {
        return await callCLI(['test', 'email']);
    },
};

export default backend;
