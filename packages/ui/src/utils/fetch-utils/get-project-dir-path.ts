import { documentDir, join } from '@tauri-apps/api/path';
import { split, tail } from 'lodash';

async function getProjectDirPath() {
    if (import.meta.env.VITE_PYRA_DIRECTORY !== undefined) {
        return await join(
            await documentDir(),
            ...tail(split(import.meta.env.VITE_PYRA_DIRECTORY, '/Documents/'))
        );
    } else {
        return await join(await documentDir(), 'pyra', `pyra-${APP_VERSION}`);
    }
}

export default getProjectDirPath;
