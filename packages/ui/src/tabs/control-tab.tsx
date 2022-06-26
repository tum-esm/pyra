import { backend, reduxUtils } from '../utils';
import { essentialComponents } from '../components';
import { useState } from 'react';
import { customTypes } from '../custom-types';
import { ICONS } from '../assets';
import toast from 'react-hot-toast';

export default function ControlTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.content);
    const plcIsControlledByUser = reduxUtils.useTypedSelector(
        (s) => s.config.central?.tum_plc?.controlled_by_user
    );

    const dispatch = reduxUtils.useTypedDispatch();
    const setConfigsPartial = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setConfigsPartial(c));

    const [isSaving, setIsSaving] = useState(false);

    async function setPlcIsControlledByUser(v: boolean) {
        setIsSaving(true);
        const update = { tum_plc: { controlled_by_user: v } };
        let result = await backend.updateConfig(update);
        if (!result.stdout.includes('Updated config file')) {
            console.error(
                `Could not update config file. processResult = ${JSON.stringify(result)}`
            );
            toast.error(`Could not update config file, please look in the console for details`);
        } else {
            setConfigsPartial(update);
        }
        setIsSaving(false);
    }

    if (coreState === undefined || plcIsControlledByUser === undefined) {
        return <></>;
    }
    return (
        <div className={'w-full relative px-6 py-6 flex-col-left gap-y-4'}>
            <div className="flex-row-left gap-x-2">
                <div>PLC is controlled by:</div>
                <essentialComponents.Toggle
                    value={plcIsControlledByUser ? 'user' : 'automation'}
                    values={['user', 'automation']}
                    setValue={(v) => setPlcIsControlledByUser(v === 'user')}
                />
                {isSaving && <essentialComponents.Spinner />}
                {!isSaving && (
                    <div className="text-sm text-gray-500 flex-row-center">
                        <div className="w-4 h-4 mr-1">{ICONS.info}</div>
                        {plcIsControlledByUser && 'The automation will skip all PLC related logic'}
                        {!plcIsControlledByUser && 'You cannot send any commands to the PLC'}
                    </div>
                )}
            </div>
            <div className="w-full h-px my-0 bg-slate-300" />
            <div className="flex flex-col w-full text-sm gap-y-4">
                <div className="relative flex overflow-hidden elevated-panel">
                    <div className="block w-48 px-4 py-2 -m-px text-base font-semibold text-white rounded-l bg-slate-900 flex-row-center">
                        Errors
                    </div>
                    <div className="flex-grow px-4 py-2 flex-row-left gap-x-4">
                        <div className="flex-col-left">
                            <div>
                                Reset needed:{' '}
                                <span className="text-base font-medium">
                                    {coreState.enclosure_plc_readings.state.reset_needed
                                        ? 'Yes'
                                        : 'No'}
                                </span>
                            </div>
                            <div>
                                Motor failed:{' '}
                                <span className="text-base font-medium">
                                    {coreState.enclosure_plc_readings.state.motor_failed
                                        ? 'Yes'
                                        : 'No'}
                                </span>
                            </div>
                        </div>
                        <div className="flex-grow flex-col-right">
                            <essentialComponents.Button
                                variant="flat-blue"
                                onClick={() => {}}
                                spinner
                            >
                                reset now
                            </essentialComponents.Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
