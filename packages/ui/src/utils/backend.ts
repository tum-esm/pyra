import { Command, ChildProcess } from '@tauri-apps/api/shell';
import TYPES from './types';

const generateCliInvocation = (cmd: string, args: string[]) =>
    new Command(cmd, ['packages/cli/main.py', ...args], {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    });

const backend = {
    readInfoLogs: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-logs-read-info', [
            'logs',
            'read',
            '--level',
            'INFO',
        ]);
        return await command.execute();
    },
    readDebugLogs: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-logs-read-debug', [
            'logs',
            'read',
            '--level',
            'DEBUG',
        ]);
        return await command.execute();
    },
    archiveLogs: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-logs-archive', [
            'logs',
            'archive',
        ]);
        return await command.execute();
    },
    startPyraCore: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-core-start', ['core', 'start']);
        return await command.execute();
    },
    pyraCliIsAvailable: async (): Promise<boolean> => {
        const command = generateCliInvocation('pyra-cli', []);
        const p = await command.execute();
        console.log(
            JSON.stringify({ p, VITE_PROJECT_DIR: import.meta.env.VITE_PROJECT_DIR })
        );
        return p.stdout.includes('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...');
    },
    checkPyraCoreState: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-core-is-running', [
            'core',
            'is-running',
        ]);
        return await command.execute();
    },
    stopPyraCore: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-core-stop', ['core', 'stop']);
        return await command.execute();
    },
    getConfig: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-config-get', ['config', 'get']);
        return await command.execute();
    },
    updateConfig: async (newConfig: TYPES.partialConfig): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-config-update', [
            'config',
            'update',
            JSON.stringify(newConfig),
        ]);
        return await command.execute();
    },
    getState: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-state-get', ['state', 'get']);
        return await command.execute();
    },
};

export default backend;
