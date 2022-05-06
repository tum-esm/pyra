import { shell, ipcMain, dialog } from 'electron';
import util from 'util';
import child_process from 'child_process';
import TYPES from './types/index';
const exec = util.promisify(child_process.exec);

// TODO: Set corrent path on windows/unix (Fixed path required on every system)
const PYRA_ROOT_DIRECTORY = '/Users/moritz/Documents/research/pyra';
const PYRA_CLI_COMMAND = `${PYRA_ROOT_DIRECTORY}/.venv/bin/python ${PYRA_ROOT_DIRECTORY}/packages/cli/main.py`;

// Check if pyra-cli command exists
async function check_pyra_cli(): Promise<boolean> {
    const { stdout } = await exec(PYRA_CLI_COMMAND, {
        shell: '/bin/bash',
        windowsHide: true,
    });
    return stdout.startsWith('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...');
}

async function call_pyra_cli(command: string): Promise<string> {
    return (
        await exec(`${PYRA_CLI_COMMAND} ${command}`, {
            shell: '/bin/bash',
            windowsHide: true,
        })
    ).stdout;
}

export function initIPCHandlers() {
    ipcMain.handle('checkCLIStatus', async (_, args) => {
        try {
            return await check_pyra_cli();
        } catch {
            return false;
        }
    });

    ipcMain.handle('readInfoLogs', async (_, args) => {
        return (await call_pyra_cli('logs read --level INFO'))
            .split('\n')
            .filter(l => l.length > 0)
            .join('\n');
    });
    ipcMain.handle('readDebugLogs', async (_, args) => {
        return (await call_pyra_cli('logs read --level DEBUG'))
            .split('\n')
            .filter(l => l.length > 0)
            .join('\n');
    });
    ipcMain.handle('archiveLogs', async (_, args) => {
        const result = await dialog.showMessageBox({
            message: 'Do you want to archive the logs?',
            type: 'warning',
            buttons: ['Yes', 'No'],
        });
        if (result.response === 0) {
            call_pyra_cli('logs archive');
        }
    });
    ipcMain.handle('selectPath', async (_, args) => {
        return dialog.showOpenDialogSync({
            properties: ['openFile', 'openDirectory', 'showHiddenFiles'],
        });
    });

    ipcMain.handle('playBeep', (_, args) => {
        shell.beep();
    });

    ipcMain.handle('readSetupJSON', async (_, args) => {
        return JSON.parse(await call_pyra_cli('config setup get'));
    });
    ipcMain.handle(
        'saveSetupJSON',
        async (_, newSetupJSON: TYPES.configJSON) => {
            return await call_pyra_cli(
                `config setup set --content "${JSON.stringify(
                    newSetupJSON
                ).replace(/"/g, '\\"')}"`
            );
        }
    );

    ipcMain.handle('readParametersJSON', async (_, args) => {
        return JSON.parse(await call_pyra_cli('config parameters get'));
    });
    ipcMain.handle(
        'saveParametersJSON',
        async (_, newParametersJSON: TYPES.configJSON) => {
            const command = `config parameters set --content "${JSON.stringify(
                newParametersJSON
            ).replace(/"/g, '\\"')}"`;
            console.log({ command });
            return await call_pyra_cli(command);
        }
    );
}
