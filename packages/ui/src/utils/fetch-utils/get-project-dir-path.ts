import { documentDir, join, downloadDir } from '@tauri-apps/api/path';

async function getProjectDirPath() {
    let projectDirPath = await join(await documentDir(), 'pyra-4');
    switch (import.meta.env.VITE_ENVIRONMENT) {
        // on my personal machine
        case 'development-moritz':
            projectDirPath = await join(await documentDir(), 'research', 'pyra-4');
            break;

        // on the R19 laptop the Documents folder is a network directory
        // hence, we cannot use that one since some script do not run there
        case 'development-R19':
            projectDirPath = await join(await downloadDir(), 'pyra-4');
            break;
    }
    return projectDirPath;
}

export default getProjectDirPath;
