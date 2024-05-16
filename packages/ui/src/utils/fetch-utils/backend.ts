import { Command, ChildProcess } from '@tauri-apps/api/shell';
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
        new Command(pythonInterpreter, [pyraCLIEntrypoint, ...args], {
            cwd: projectDirPath,
        }).execute().then((result) => {
            resolve(result);
        }).catch((error) => {
            console.error("Error when calling CLI: ", error);
            reject(error);
        });
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
    testOpus: async (): Promise<ChildProcess> => {
        return await callCLI(['test', 'opus']);
    },
    testCamTracker: async (): Promise<ChildProcess> => {
        return await callCLI(['test', 'camtracker']);
    },
    testEmail: async (): Promise<ChildProcess> => {
        return await callCLI(['test', 'email']);
    },
    testUpload: async (): Promise<ChildProcess> => {
        return await callCLI(['test', 'upload']);
    },
};

export default backend;
