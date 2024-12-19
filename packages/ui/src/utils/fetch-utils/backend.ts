import { Command, ChildProcess } from '@tauri-apps/plugin-shell';
import { join } from '@tauri-apps/api/path';
import fetchUtils from '.';

async function callCLI(args: string[]): Promise<ChildProcess<string>> {
    let projectDirPath = await fetchUtils.getProjectDirPath();
    let pythonInterpreter =
        import.meta.env.VITE_PYTHON_INTERPRETER === 'venv' ? 'venv-python' : 'system-python';
    let pyraCLIEntrypoint = await join('packages', 'cli', 'main.py');

    const commandString = [pythonInterpreter, pyraCLIEntrypoint, ...args].join(' ');
    console.debug(`Running shell command: "${commandString}" in directory "${projectDirPath}"`);

    return new Promise(async (resolve, reject) => {
        Command.create(pythonInterpreter, [pyraCLIEntrypoint, ...args], {
            cwd: projectDirPath,
        })
            .execute()
            .then((result) => {
                if (result.code === 0) {
                    console.debug('CLI command executed successfully');
                    resolve(result);
                } else {
                    console.error('Error when calling CLI: ', result);
                    reject(result);
                }
            })
            .catch((error) => {
                console.error('Error when calling CLI: ', error);
                reject(error);
            });
    });
}

const backend = {
    pyraCliIsAvailable: async (): Promise<ChildProcess<string>> => {
        return await callCLI([]);
    },
    checkPyraCoreState: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['core', 'is-running']);
    },
    startPyraCore: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['core', 'start']);
    },
    stopPyraCore: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['core', 'stop']);
    },
    getConfig: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['config', 'get', '--no-indent', '--no-color']);
    },
    updateConfig: async (newConfig: any): Promise<ChildProcess<string>> => {
        return await callCLI(['config', 'update', JSON.stringify(newConfig)]);
    },
    writeToTUMEnclosure: async (command: string[]): Promise<ChildProcess<string>> => {
        return await callCLI(['tum-enclosure', ...command]);
    },
    testOpus: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['test', 'opus']);
    },
    testCamTracker: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['test', 'camtracker']);
    },
    testEmail: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['test', 'email']);
    },
    testUpload: async (): Promise<ChildProcess<string>> => {
        return await callCLI(['test', 'upload']);
    },
};

export default backend;
