import { essentialComponents } from '..';

const linkToInstallationInstructions = (
    <>
        Please following the installation instructions on{' '}
        <span className="font-bold text-blue-500 underline">https://github.com/tum-esm/pyra</span>.
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

    return (
        <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
            <div className="inline max-w-sm text-center">
                {backendIntegrity === 'cli is missing' && (
                    <>
                        <strong>pyra-cli</strong> has not been found on your system.{' '}
                        {linkToInstallationInstructions}
                    </>
                )}
                {backendIntegrity === 'config is invalid' && (
                    <>
                        The file <strong>config.json</strong> is not in a valid JSON format.{' '}
                        {linkToInstallationInstructions}
                    </>
                )}
                {backendIntegrity === 'pyra-core is not running' && (
                    <>
                        <strong>pyra-core</strong> is not running.
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
            >
                {backendIntegrity === 'pyra-core is not running'
                    ? 'start pyra-core'
                    : 'retry connection'}
            </essentialComponents.Button>
        </main>
    );
}
