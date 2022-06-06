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

const backend = {
    isAvailable: async (): Promise<boolean> => await invoke('cli_is_available'),
    readInfoLogs: async (): Promise<string[]> => await invoke('read_info_logs'),
    readDebugLogs: async (): Promise<string[]> => await invoke('read_debug_logs'),
    archiveLogs: async (): Promise<string[]> => await invoke('archive_logs'),
    readConfig: async (): Promise<TYPES.config> => await invoke('read_config'),
    updateConfig: async (newConfig: TYPES.config): Promise<string[]> =>
        await invoke('update_config', {
            newJsonString: JSON.stringify(newConfig).replace(/"/g, '\\"'),
        }),
    startPyraCore: async (): Promise<ChildProcess> => {
        const command = new Command(
            'pyra-cli-core-start',
            ['packages/cli/main.py', 'core', 'start'],
            {
                cwd: import.meta.env.VITE_PROJECT_DIR,
            }
        );
        return await command.execute();
    },
    checkPyraCoreState: async (): Promise<ChildProcess> => {
        const command = new Command(
            'pyra-cli-core-is-running',
            ['packages/cli/main.py', 'core', 'is-running'],
            {
                cwd: import.meta.env.VITE_PROJECT_DIR,
            }
        );
        return await command.execute();
    },
    stopPyraCore: async (): Promise<ChildProcess> => {
        const command = new Command(
            'pyra-cli-core-stop',
            ['packages/cli/main.py', 'core', 'stop'],
            {
                cwd: import.meta.env.VITE_PROJECT_DIR,
            }
        );
        return await command.execute();
    },
};

export default backend;
