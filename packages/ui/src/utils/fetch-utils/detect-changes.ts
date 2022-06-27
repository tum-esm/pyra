import toast from 'react-hot-toast';
import { shell } from '@tauri-apps/api';
import { first } from 'lodash';

async function detectFileChanges(
    oldChecksums: { logs: string; coreState: string; config: string },
    setLogsShouldBeLoaded: (v: boolean) => void,
    setCoreStateShouldBeLoaded: (v: boolean) => void,
    setConfigShouldBeLoaded: (v: boolean) => void,
    setChecksums: (v: { logs: string; coreState: string; config: string }) => void
) {
    let cmd = 'md5-windows';
    let filepaths = ['logs\\debug.log', 'runtime-data\\state.json', 'config\\config.json'];
    if (window.navigator.platform.includes('Mac')) {
        cmd = 'md5-mac';
        filepaths = filepaths.map((p) => p.replace('\\', '/'));
    }

    const result = await new shell.Command(cmd, filepaths, {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    }).execute();

    if (result.code !== 0 && !result.stderr.includes('state.json: No such file')) {
        toast.error('File watcher is not working - details in console');
        console.error(`File watcher is not working, processResult = ${JSON.stringify(result)}`);
        return;
    }

    const getLine = (indicator: string) => {
        const line = first(result.stdout.split('\n').filter((line) => line.includes(indicator)));
        return line || '';
    };

    let checksumsChanged = false;

    const newLogsChecksum = getLine('debug.log');
    if (newLogsChecksum !== oldChecksums.logs) {
        if (oldChecksums.logs !== '') {
            setLogsShouldBeLoaded(true);
            console.log('change in log files detected');
        }
        checksumsChanged = true;
    }

    const newStateChecksum = getLine('state.json');
    if (newStateChecksum !== oldChecksums.coreState) {
        if (oldChecksums.coreState !== '') {
            setCoreStateShouldBeLoaded(true);
            console.log('change in core state file detected');
        }
        checksumsChanged = true;
    }

    const newConfigChecksum = getLine('config.json');
    if (newConfigChecksum !== oldChecksums.config) {
        if (oldChecksums.config !== '') {
            // wait 2 second to make sure all state changes have propagated
            setTimeout(() => setConfigShouldBeLoaded(true), 2000);
            console.log('change in config file detected');
        }
        checksumsChanged = true;
    }

    if (checksumsChanged) {
        setChecksums({
            logs: newLogsChecksum,
            coreState: newStateChecksum,
            config: newConfigChecksum,
        });
    }
}

export default detectFileChanges;
