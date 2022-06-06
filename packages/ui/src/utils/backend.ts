import { Command, ChildProcess } from '@tauri-apps/api/shell';
import { invoke as invokeTauriCommand } from '@tauri-apps/api/tauri';
import { trim } from 'lodash';
import TYPES from './types';

async function invoke(command: string, argument?: object): Promise<any> {
    /* @ts-ignore */
    const result = await invokeTauriCommand(command, argument);
    if (typeof result === 'string') {
        if (command.includes('json') && command.includes('read')) {
            return JSON.parse(result);
        } else {
            return trim(result.replace(/\n+/g, '\n'), '\n').split('\n');
        }
    } else {
        return result === true;
    }
}

const generateCliInvocation = (cmd: string, args: string[]) =>
    new Command(cmd, ['packages/cli/main.py', ...args], {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    });

const backend = {
    readInfoLogs: async (): Promise<string[]> => await invoke('read_info_logs'),
    readDebugLogs: async (): Promise<string[]> => await invoke('read_debug_logs'),
    archiveLogs: async (): Promise<string[]> => await invoke('archive_logs'),
    startPyraCore: async (): Promise<ChildProcess> => {
        const command = generateCliInvocation('pyra-cli-core-start', ['core', 'start']);
        return await command.execute();
    },
    pyraCliIsAvailable: async (): Promise<boolean> => {
        const command = generateCliInvocation('pyra-cli', []);
        const p = await command.execute();
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
};

export default backend;
