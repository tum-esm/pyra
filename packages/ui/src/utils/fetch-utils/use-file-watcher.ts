import { shell } from '@tauri-apps/api';
import { useEffect, useState } from 'react';

async function getChecksum(filepath: string) {
    let command = 'md5-windows';
    if (window.navigator.platform.includes('Mac')) {
        command = 'md5-mac';
        filepath = filepath.replace('\\', '/');
    }

    const commandOutput = await new shell.Command(command, filepath, {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    }).execute();

    return commandOutput.stdout.replace(/\n/g, '');
}

async function getFileContent(filepath: string) {
    if (window.navigator.platform.includes('Mac')) {
        filepath = filepath.replace('\\', '/');
    }

    const commandOutput = await new shell.Command('cat', filepath, {
        cwd: import.meta.env.VITE_PROJECT_DIR,
    }).execute();

    return commandOutput.stdout;
}

function useFileWatcher(filepath: string, intervalSeconds: number): [string | undefined, boolean] {
    const [isLoading, setIsLoading] = useState(false);
    const [checksum, setChecksum] = useState('');
    const [fileContent, setFileContent] = useState<undefined | string>(undefined);

    let hash_command = 'md5-windows';
    if (window.navigator.platform.includes('Mac')) {
        hash_command = 'md5-mac';
        filepath = filepath.replace('\\', '/');
    }

    useEffect(() => {
        const watchInterval = setInterval(async () => {
            const newChecksum = await getChecksum(filepath);
            if (checksum !== newChecksum) {
                setIsLoading(true);
                setChecksum(newChecksum);
            }
        }, intervalSeconds * 1000);
        return () => clearInterval(watchInterval);
    });

    useEffect(() => {
        async function updateFile() {
            const newFileContent = await getFileContent(filepath);
            setFileContent(newFileContent);
            setIsLoading(false);
        }
        updateFile();
    }, [checksum]);

    return [fileContent, isLoading];
}

export default useFileWatcher;
