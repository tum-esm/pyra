import { useEffect, useState } from 'react';
import { ICONS } from './assets';
import { structuralComponents } from './components';
import Dashboard from './components/structural/dashboard';
import toast, { Toaster } from 'react-hot-toast';
import backend from './utils/fetch-utils/backend';

export default function Main() {
    const [backendIntegrity, setBackendIntegrity] = useState<
        undefined | 'valid' | 'cli is missing'
    >(undefined);

    useEffect(() => {
        load();
    }, []);

    function load() {
        if (backendIntegrity !== 'valid') {
            toast.promise(backend.pyraCliIsAvailable(), {
                loading: 'Connecting to Pyra backend',
                success: () => {
                    setBackendIntegrity('valid');
                    return 'Found Pyra on your system';
                },
                error: () => {
                    setBackendIntegrity('cli is missing');
                    return 'Could not find Pyra on your system';
                },
            });
        }
    }

    return (
        <div className="relative flex flex-col items-stretch w-screen h-screen overflow-hidden">
            {backendIntegrity === undefined && (
                <>
                    <structuralComponents.BlankHeader />
                    <main className="w-full h-full flex-row-center">
                        <div className="w-8 h-8 text-slate-950 animate-spin">{ICONS.spinner}</div>
                    </main>
                </>
            )}
            {backendIntegrity === 'cli is missing' && (
                <structuralComponents.DisconnectedScreen retry={load} />
            )}
            {backendIntegrity === 'valid' && <Dashboard />}
            <Toaster position="bottom-right" />
        </div>
    );
}
