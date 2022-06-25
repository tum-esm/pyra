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
                <essentialComponents.Toggle
                    value={
                        plcIsControlledByUser
                            ? 'PLC is controlled by user'
                            : 'PLC is controlled by automation'
                    }
                    values={['PLC is controlled by user', 'PLC is controlled by automation']}
                    setValue={(v) => setPlcIsControlledByUser(v === 'PLC is controlled by user')}
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
            <div className="w-full break-all">{JSON.stringify(coreState)}</div>
        </div>
    );
}
