import { ChildProcess } from '@tauri-apps/api/shell';
import { useLogsStore } from '../zustand-utils/logs-zustand';
import toast from 'react-hot-toast';

export default function useCommand() {
    const { addUiLogLine } = useLogsStore();

    function exitFromFailedProcess(p: ChildProcess, label: string): string {
        addUiLogLine(`Error while ${label}.`, `stdout = ${p.stdout}, stderr = ${p.stderr}`);
        return `Error while ${label}, full error in UI logs`;
    }

    function runPromisingCommand(args: {
        command: () => Promise<ChildProcess>;
        label: string;
        successLabel: string;
        onSuccess?: (p: ChildProcess) => void;
        onError?: (p: ChildProcess) => void;
    }): void {
        toast.promise(args.command(), {
            loading: args.label,
            success: (p: ChildProcess) => {
                if (args.onSuccess) {
                    args.onSuccess(p);
                }
                return args.successLabel;
            },
            error: (p: ChildProcess) => {
                if (args.onError) {
                    args.onError(p);
                }
                return exitFromFailedProcess(p, args.label);
            },
        });
    }

    return {
        runPromisingCommand,
    };
}
