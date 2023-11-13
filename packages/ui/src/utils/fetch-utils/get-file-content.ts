import { readBinaryFile } from '@tauri-apps/api/fs';
import { BaseDirectory, join } from '@tauri-apps/api/path';

async function getFileContent(filePath: string): Promise<string> {
    let baseDir: 7 | 8;
    let absoluteFilePath: string;
    switch (import.meta.env.VITE_ENVIRONMENT) {
        // on moritz personal machine
        case 'development-moritz':
            baseDir = BaseDirectory.Document;
            absoluteFilePath = await join('work', 'esm', 'pyra', ...filePath.split('/'));
            break;

        // on the R19 laptop the Documents folder is a network directory
        // hence, we cannot use that one since some script do not run there
        case 'development-R19':
            baseDir = BaseDirectory.Download;
            absoluteFilePath = await join('pyra', `pyra-${APP_VERSION}`, ...filePath.split('/'));
            break;

        // on all other systems (no development of PYRA)
        default:
            baseDir = BaseDirectory.Document;
            absoluteFilePath = await join('pyra', `pyra-${APP_VERSION}`, ...filePath.split('/'));
            break;
    }
    console.debug(
        `Reading file: "~/${
            baseDir === BaseDirectory.Document ? 'Documents' : 'Downloads'
        }/${absoluteFilePath}"`
    );
    const binaryContent = await readBinaryFile(absoluteFilePath, { dir: baseDir });

    return new TextDecoder('utf-8').decode(binaryContent);
}

export default getFileContent;
