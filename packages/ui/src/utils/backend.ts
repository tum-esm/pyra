import { invoke as invokeTauriCommand } from '@tauri-apps/api/tauri';
import { trim } from 'lodash';

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
    readSetupJSON: async (): Promise<object> => await invoke('read_setup_json'),
    readParametersJSON: async (): Promise<object> =>
        await invoke('read_parameters_json'),
    updateSetupJSON: async (newConfig: object): Promise<string[]> =>
        await invoke('update_setup_json', {
            newJsonString: JSON.stringify(newConfig).replace(/"/g, '\\"'),
        }),
    updateParamtersJSON: async (newConfig: object): Promise<string[]> =>
        await invoke('update_parameters_json', {
            newJsonString: JSON.stringify(newConfig),
        }),
};

export default backend;
