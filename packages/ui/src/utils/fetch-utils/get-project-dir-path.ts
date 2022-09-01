import { documentDir, join, downloadDir } from '@tauri-apps/api/path';

async function getProjectDirPath() {
    let projectDirPath: string;
    switch (import.meta.env.VITE_ENVIRONMENT) {
        // on moritz personal machine
        case 'development-moritz':
            projectDirPath = await join(await documentDir(), 'research', 'pyra-4');
            break;

        // on the R19 laptop the Documents folder is a network directory
        // hence, we cannot use that one since some script do not run there
        case 'development-R19':
            projectDirPath = await join(await downloadDir(), 'pyra-4');
            break;

        // on all other systems (no development of PYRA)
        default:
            projectDirPath = await join(await documentDir(), 'pyra', `pyra-${APP_VERSION}`);
            break;
    }
    return projectDirPath;
}

export default getProjectDirPath;
