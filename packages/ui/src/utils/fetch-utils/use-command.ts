import { ChildProcess } from '@tauri-apps/plugin-shell';
import { useLogsStore } from '../zustand-utils/logs-zustand';
import toast from 'react-hot-toast';
import { useState } from 'react';

export default function useCommand() {
    const { addUiLogLine } = useLogsStore();
    const [commandIsRunning, setCommandIsRunning] = useState(false);

    function exitFromFailedProcess(p: ChildProcess<string>, label: string): string {
        addUiLogLine(
            `Error while ${label}.`,
            `stdout: "${p.stdout.trim()}"\nstderr: "${p.stderr.trim()}"`
        );
        return `Error while ${label}, full error in UI logs`;
    }

    function runPromisingCommand(args: {
        command: () => Promise<ChildProcess<string>>;
        label: string;
        successLabel: string;
        onSuccess?: (p: ChildProcess<string>) => void;
        onError?: (p: ChildProcess<string>) => void;
    }): void {
        if (commandIsRunning) {
            toast.error('Cannot run multiple commands at the same time');
        } else {
            setCommandIsRunning(true);
            toast.promise(args.command(), {
                loading: args.label,
                success: (p: ChildProcess<string>) => {
                    if (args.onSuccess) {
                        args.onSuccess(p);
                    }
                    setCommandIsRunning(false);
                    return args.successLabel;
                },
                error: (p: ChildProcess<string>) => {
                    if (args.onError) {
                        args.onError(p);
                    }
                    setCommandIsRunning(false);
                    return exitFromFailedProcess(p, args.label);
                },
            });
        }
    }

    return {
        commandIsRunning,
        runPromisingCommand,
    };
}
