import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { fetchUtils, reduxUtils } from './utils';
import { structuralComponents } from './components';
import Dashboard from './components/structural/dashboard';
import { usePyraCoreStore } from './utils/zustand-utils/core-state-zustand';
import { Toaster } from 'react-hot-toast';

export default function Main() {
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing' | 'config is invalid' | 'pyra-core is not running'
    >(undefined);

    const dispatch = reduxUtils.useTypedDispatch();

    const { pyraCorePid, setPyraCorePid } = usePyraCoreStore();

    useEffect(() => {
        if (pyraCorePid === -1 && backendIntegrity == 'valid') {
            setBackendIntegrity('pyra-core is not running');
        }
    }, [backendIntegrity, pyraCorePid]);

    async function startPyraCore(): Promise<void> {
        setPyraCorePid(undefined);
        try {
            const p = await fetchUtils.backend.startPyraCore();
            const pid = parseInt(p.stdout.replace(/[^\d]/g, ''));
            setPyraCorePid(pid);
            setBackendIntegrity('valid');
        } catch {
            setPyraCorePid(undefined);
            throw 'could not start pyra core';
        }
    }

    useEffect(() => {
        fetchUtils
            .initialAppState(dispatch, setBackendIntegrity, setPyraCorePid)
            .catch(console.error);
    }, []);

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
                        fetchUtils.initialAppState(dispatch, setBackendIntegrity, setPyraCorePid)
                    }
                    startPyraCore={startPyraCore}
                />
            )}
            {backendIntegrity === 'valid' && <Dashboard />}
            <Toaster position="bottom-right" />
        </div>
    );
}
