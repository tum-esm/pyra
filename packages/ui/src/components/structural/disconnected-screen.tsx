import { useEffect, useState } from 'react';
import { fetchUtils } from '../../utils';
import { Button } from '../ui/button';

const LinkToInstallationInstructions = (props: { projectDirPath: string }) => (
    <>
        Please follow the installation instructions on{' '}
        <span className="font-bold text-blue-500 underline">https://github.com/tum-esm/pyra</span>.
        PYRA 4 should be located at "{props.projectDirPath}"
    </>
);

export default function DisconnectedScreen(props: { retry: () => void }) {
    const [projectDirPath, setProjectDirPath] = useState('');

    useEffect(() => {
        async function init() {
            setProjectDirPath(await fetchUtils.getProjectDirPath());
        }

        init();
    }, []);

    return (
        <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
            <div className="inline max-w-lg text-center">
                PYRA has not been found on your system.{' '}
                <LinkToInstallationInstructions projectDirPath={projectDirPath} />
            </div>
            <Button onClick={props.retry}>try again</Button>
        </main>
    );
}
