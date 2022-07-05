import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { fetchUtils, reduxUtils } from './utils';
import { structuralComponents } from './components';
import Dashboard from './components/structural/dashboard';

export default function Main() {
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid'
    >(undefined);

    const dispatch = reduxUtils.useTypedDispatch();

    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
    const pyraCoreIsRunning = pyraCorePID !== undefined && pyraCorePID !== -1;

    useEffect(() => {
        fetchUtils.initialAppState(dispatch, setBackendIntegrity).catch(console.error);
    }, []);

    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    let enclosureControlsIsVisible =
        centralConfig === undefined ? undefined : centralConfig.tum_plc !== null;
    // TODO: show "reload required" popup if "enclosureControlsIsVisible" changes
    // to true or false

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {backendIntegrity === undefined && (
                <main className="w-full h-full flex-row-center">
                    <div className="w-8 h-8 text-green-600 animate-spin">{ICONS.spinner}</div>
                </main>
            )}
            {(backendIntegrity === 'cli is missing' ||
                backendIntegrity === 'config is invalid') && (
                <structuralComponents.DisconnectedScreen
                    backendIntegrity={backendIntegrity}
                    loadInitialAppState={() =>
                        fetchUtils.initialAppState(dispatch, setBackendIntegrity)
                    }
                />
            )}
            {backendIntegrity === 'valid' && !pyraCoreIsRunning && 'start pyra core button'}
            {backendIntegrity === 'valid' && pyraCoreIsRunning && <Dashboard />}
        </div>
    );
}
