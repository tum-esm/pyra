import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { fetchUtils, reduxUtils } from './utils';
import { structuralComponents } from './components';
import Dashboard from './components/structural/dashboard';

export default function Main() {
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid' | 'pyra-core is not running'
    >(undefined);

    const dispatch = reduxUtils.useTypedDispatch();

    const setPyraCorePID = (pid: number | undefined) =>
        dispatch(reduxUtils.coreProcessActions.set({ pid }));

    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);

    useEffect(() => {
        if (pyraCorePID === -1 && backendIntegrity == 'valid') {
            setBackendIntegrity('pyra-core is not running');
        }
    }, [backendIntegrity, pyraCorePID]);

    async function startPyraCore() {
        setPyraCorePID(undefined);
        try {
            const p = await fetchUtils.backend.startPyraCore();
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setPyraCorePID(pid);
            setBackendIntegrity('valid');
        } catch {
            // TODO: add message to queue
            setPyraCorePID(undefined);
        }
    }

    useEffect(() => {
        fetchUtils.initialAppState(dispatch, setBackendIntegrity).catch(console.error);
    }, []);

    // TODO: show "reload required" popup if "enclosureControlsIsVisible" changes to true or false
    //const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    //let enclosureControlsIsVisible =
    //    centralConfig === undefined ? undefined : centralConfig.tum_plc !== null;

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {backendIntegrity === undefined && (
                <main className="w-full h-full flex-row-center">
                    <div className="w-8 h-8 text-green-600 animate-spin">{ICONS.spinner}</div>
                </main>
            )}
            {backendIntegrity !== undefined && backendIntegrity !== 'valid' && (
                <structuralComponents.DisconnectedScreen
                    backendIntegrity={backendIntegrity}
                    loadInitialAppState={() =>
                        fetchUtils.initialAppState(dispatch, setBackendIntegrity)
                    }
                    startPyraCore={startPyraCore}
                />
            )}
            {backendIntegrity === 'valid' && <Dashboard />}
        </div>
    );
}
