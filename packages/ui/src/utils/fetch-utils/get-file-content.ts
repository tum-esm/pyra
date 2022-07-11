import { readTextFile } from '@tauri-apps/api/fs';
import { BaseDirectory, join } from '@tauri-apps/api/path';

async function getFileContent(filePath: string) {
    let baseDir = BaseDirectory.Document;
    let absoluteFilePath = await join('pyra-4', ...filePath.split('/'));
    switch (import.meta.env.VITE_ENVIRONMENT) {
        // on my personal machine
        case 'development-moritz':
            absoluteFilePath = await join('research', 'pyra-4', ...filePath.split('/'));
            break;

        // on the R19 laptop the Documents folder is a network directory
        // hence, we cannot use that one since some script do not run there
        case 'development-R19':
            baseDir = BaseDirectory.Download;
            break;
    }
    console.debug(`Reading file: "${absoluteFilePath}" in directory "${baseDir}"`);
    return await readTextFile(absoluteFilePath, { dir: baseDir });
}

export default getFileContent;
