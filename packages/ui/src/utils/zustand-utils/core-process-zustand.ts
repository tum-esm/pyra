import { create } from 'zustand';

interface CoreProcessStore {
    pyraCorePid: number | undefined;
    setPyraCorePid: (pid: number | undefined) => void;
}

export const useCoreProcessStore = create<CoreProcessStore>()((set) => ({
    pyraCorePid: undefined,
    setPyraCorePid: (pid) => set(() => ({ pyraCorePid: pid })),
}));
