import { essentialComponents } from '..';

export default function DisconnectedScreen(props: {
    backendIntegrity: undefined | 'valid' | 'cli is missing' | 'config is invalid';
    loadInitialAppState(): void;
}) {
    return (
        <main className="flex flex-col items-center justify-center w-full h-full bg-gray-100 gap-y-4">
            <p className="inline max-w-sm text-center">
                {props.backendIntegrity === 'cli is missing' && (
                    <>
                        <pre className="bg-gray-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
                            pyra-cli
                        </pre>{' '}
                        has not been found on your system.{' '}
                    </>
                )}
                {props.backendIntegrity === 'config is invalid' && (
                    <>
                        The file{' '}
                        <pre className="bg-gray-200 mr-1 px-1 py-0.5 rounded-sm text-sm inline">
                            config.json
                        </pre>{' '}
                        is not in a valid JSON format.{' '}
                    </>
                )}
                Please following the installation instructions on{' '}
                <span className="font-bold text-blue-500 underline">
                    https://github.com/tum-esm/pyra
                </span>
                .
            </p>
            <essentialComponents.Button onClick={props.loadInitialAppState} variant="green">
                retry connection
            </essentialComponents.Button>
        </main>
    );
}
