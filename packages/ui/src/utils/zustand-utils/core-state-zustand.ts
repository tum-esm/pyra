import { create } from 'zustand';

interface PyraCoreState {
    pyraCorePid: number | undefined;
    setPyraCorePid: (pid: number | undefined) => void;
}

export const usePyraCoreStore = create<PyraCoreState>()((set) => ({
    pyraCorePid: undefined,
    setPyraCorePid: (pid) => set(() => ({ pyraCorePid: pid })),
}));
