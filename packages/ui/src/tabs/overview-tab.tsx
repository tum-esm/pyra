import { fetchUtils } from '../utils';
import { essentialComponents, overviewComponents } from '../components';
import { useLogsStore } from '../utils/zustand-utils/logs-zustand';
import { useConfigStore } from '../utils/zustand-utils/config-zustand';
import { Button } from '../components/ui/button';

export default function OverviewTab() {
    const { coreLogs } = useLogsStore();
    const { runPromisingCommand } = fetchUtils.useCommand();
    const { centralConfig } = useConfigStore();

    function closeCover() {
        runPromisingCommand({
            command: () => fetchUtils.backend.writeToTUMEnclosure(['close-cover']),
            label: 'closing cover',
            successLabel: 'successfully closed cover',
        });
    }

    return (
        <div className={'flex-col-center w-full pb-4 relative overflow-x-hidden bg-slate-50'}>
            <div className="flex flex-col w-full p-4 text-sm gap-y-1">
                <overviewComponents.PyraCoreStatus />
                <overviewComponents.MeasurementDecision />
            </div>
            <div className="w-full p-4 border-t border-slate-300">
                <overviewComponents.ActivityPlot />
            </div>
            <div className="flex flex-row items-center w-full px-4 py-4 pb-2 text-base font-semibold border-t border-slate-300">
                <div>System State</div>
                <div className="flex-grow" />
                {centralConfig?.tum_enclosure && (
                    <Button onClick={closeCover} className="mt-1.5">
                        force cover close
                    </Button>
                )}
            </div>
            <overviewComponents.SystemState />
            <div className="w-full px-4 pt-3 pb-2 text-base font-semibold border-t border-slate-300">
                Recent Logs
            </div>
            <div className="w-[calc(100%-2rem)] mx-4 rounded-lg overflow-hidden font-mono text-xs bg-white border border-slate-200 py-1">
                {(coreLogs.all === undefined || coreLogs.all.length === 0) && (
                    <div className="p-2">
                        <essentialComponents.Spinner />
                    </div>
                )}
                {coreLogs.all !== undefined &&
                    coreLogs.all
                        .filter((l) => !l.includes(' - DEBUG - '))
                        .slice(-15)
                        .map((l, i) => (
                            <essentialComponents.CoreLogLine
                                key={`${i} ${l}`}
                                text={l}
                                displayInterationSeparator={false}
                            />
                        ))}
            </div>
        </div>
    );
}
