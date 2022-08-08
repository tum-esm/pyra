import { useEffect, useState } from 'react';
import { essentialComponents } from '..';
import { reduxUtils, fetchUtils } from '../../utils';

const LinkToInstallationInstructions = (props: { projectDirPath: string }) => (
    <>
        Please follow the installation instructions on{' '}
        <span className="font-bold text-blue-500 underline">https://github.com/tum-esm/pyra</span>.
        PYRA 4 should be located at "{props.projectDirPath}"
    </>
);

export default function DisconnectedScreen(props: {
    backendIntegrity:
        | undefined
        | 'cli is missing'
        | 'config is invalid'
        | 'pyra-core is not running';
    loadInitialAppState(): void;
    startPyraCore(): void;
}) {
    const { backendIntegrity } = props;
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
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
                {backendIntegrity === 'cli is missing' && (
                    <>
                        PYRA has not been found on your system.{' '}
                        <LinkToInstallationInstructions projectDirPath={projectDirPath} />
                    </>
                )}
                {backendIntegrity === 'config is invalid' && (
                    <>
                        The file <strong>config.json</strong> is not in a valid JSON format.{' '}
                        <LinkToInstallationInstructions projectDirPath={projectDirPath} />
                    </>
                )}
                {backendIntegrity === 'pyra-core is not running' && (
                    <>
                        <strong>PYRA Core</strong> is not running.
                    </>
                )}
            </div>
            <essentialComponents.Button
                onClick={
                    backendIntegrity === 'pyra-core is not running'
                        ? props.startPyraCore
                        : props.loadInitialAppState
                }
                variant="green"
                spinner={
                    backendIntegrity === 'pyra-core is not running' && pyraCorePID === undefined
                }
            >
                {backendIntegrity === 'pyra-core is not running'
                    ? 'start core'
                    : 'retry connection'}
            </essentialComponents.Button>
        </main>
    );
}
