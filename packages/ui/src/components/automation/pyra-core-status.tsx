import { fetchUtils, reduxUtils } from '../../utils';
import { essentialComponents } from '..';

export default function PyraCoreStatus() {
    const pyraCorePID = reduxUtils.useTypedSelector((s) => s.coreProcess.pid);
    const dispatch = reduxUtils.useTypedDispatch();
    const setPyraCorePID = (pid: number | undefined) =>
        dispatch(reduxUtils.coreProcessActions.set({ pid }));

    async function stopPyraCore() {
        setPyraCorePID(undefined);
        await fetchUtils.backend.stopPyraCore();
        setPyraCorePID(-1);
    }

    return (
        <div className={'w-full text-sm flex-row-left gap-x-2 p-4'}>
            <div className="flex-grow text-sm h-7 flex-row-left">
                <essentialComponents.Ping state={true} />
                <span className="ml-2.5 mr-1">
                    Pyra Core is running with process ID {pyraCorePID}
                </span>
            </div>
            <essentialComponents.Button
                onClick={stopPyraCore}
                variant={'red'}
                spinner={pyraCorePID === undefined}
            >
                stop Pyra Core
            </essentialComponents.Button>
        </div>
    );
}
