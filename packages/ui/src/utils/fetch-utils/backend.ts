import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { customTypes } from '../../custom-types';
import { join } from '@tauri-apps/api/path';
import fetchUtils from '.';

async function callCLI(args: string[]): Promise<ChildProcess> {
    let projectDirPath = await fetchUtils.getProjectDirPath();

    let pythonInterpreter =
        import.meta.env.VITE_ENVIRONMENT === 'development-moritz' ? 'venv-python' : 'system-python';
    let pyraCLIEntrypoint = await join('packages', 'cli', 'main.py');

    const commandString = [pythonInterpreter, pyraCLIEntrypoint, ...args].join(' ');
    console.debug(`Running shell command: "${commandString}" in directory "${projectDirPath}"`);

    return new Promise(async (resolve, reject) => {
        console.log('c');
        const result = await new Command(pythonInterpreter, [pyraCLIEntrypoint, ...args], {
            cwd: projectDirPath,
        }).execute();
        console.log('d');

        if (result.code === 0) {
            resolve(result);
        } else {
            reject(result);
        }
    });
}

const backend = {
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
        return await callCLI(['config', 'get', '--no-indent', '--no-color']);
    },
    updateConfig: async (newConfig: customTypes.partialConfig): Promise<ChildProcess> => {
        return await callCLI(['config', 'update', JSON.stringify(newConfig)]);
    },
    writeToPLC: async (command: string[]): Promise<ChildProcess> => {
        return await callCLI(['plc', ...command]);
    },
};

export default backend;
