import { customTypes } from '../../../custom-types';
import { ICONS } from '../../../assets';
import { configurationComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionErrorEmail() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.error_email);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.error_email);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementToggle
                title="Notify Recipients"
                value={localSectionConfig.notify_recipients}
                setValue={(v: boolean) => update({ error_email: { notify_recipients: v } })}
                oldValue={centralSectionConfig.notify_recipients}
            />
            <configurationComponents.ConfigElementText
                title="Sender Address"
                value={localSectionConfig.sender_address}
                setValue={(v: string) => update({ error_email: { sender_address: v } })}
                oldValue={centralSectionConfig.sender_address}
            />
            <configurationComponents.ConfigElementText
                title="Sender Password"
                value={localSectionConfig.sender_password}
                setValue={(v: string) => update({ error_email: { sender_password: v } })}
                oldValue={centralSectionConfig.sender_password}
            />
            <configurationComponents.ConfigElementText
                title="Recipients"
                value={localSectionConfig.recipients}
                setValue={(v: string) => update({ error_email: { recipients: v } })}
                oldValue={centralSectionConfig.recipients}
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>Add multiple recipient
                emails by splitting them with a comma.
            </div>
        </>
    );
}
