import { readBinaryFile } from '@tauri-apps/plugin-fs';
import { BaseDirectory, join } from '@tauri-apps/api/path';
import { split, tail } from 'lodash';

async function getFileContent(filePath: string): Promise<string> {
    let absoluteFilePath: string;

    if (import.meta.env.VITE_PYRA_DIRECTORY !== undefined) {
        absoluteFilePath = await join(
            ...tail(split(import.meta.env.VITE_PYRA_DIRECTORY, '/Documents/')),
            ...filePath.split('/')
        );
    } else {
        absoluteFilePath = await join('pyra', `pyra-${APP_VERSION}`, ...filePath.split('/'));
    }

    console.debug(`Reading file: "${absoluteFilePath}" in ~/Documents`);
    return new TextDecoder('utf-8').decode(
        await readBinaryFile(absoluteFilePath, { dir: BaseDirectory.Document })
    );
}

export default getFileContent;
