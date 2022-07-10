import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { customTypes } from '../../custom-types';
import { documentDir, join, downloadDir } from '@tauri-apps/api/path';

async function callCLI(args: string[]) {
    let projectDirPath = await join(await documentDir(), 'pyra-4');
    switch (import.meta.env.VITE_ENVIRONMENT) {
        // on my personal machine
        case 'development-moritz':
            projectDirPath = await join(await documentDir(), 'research', 'pyra');
            break;

        // on the R19 laptop the Documents folder is a network directory
        // hence, we cannot use that one since some script do not run there
        case 'development-R19':
            projectDirPath = await join(await downloadDir(), 'pyra-4');
            break;
    }

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
