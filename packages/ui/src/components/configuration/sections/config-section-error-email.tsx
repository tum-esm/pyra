import { ICONS } from '../../../assets';
import { configurationComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';

export default function ConfigSectionErrorEmail() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.error_email;
    const localSectionConfig = localConfig?.error_email;

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementToggle
                title="Send Error Emails"
                value={localSectionConfig.notify_recipients}
                setValue={(v: boolean) => setLocalConfigItem('error_email.notify_recipients', v)}
                oldValue={centralSectionConfig.notify_recipients}
            />
            <configurationComponents.ConfigElementText
                title="SMTP Host"
                value={localSectionConfig.smtp_host}
                setValue={(v: string) => setLocalConfigItem('error_email.smtp_host', v)}
                oldValue={centralSectionConfig.smtp_host}
            />
            <configurationComponents.ConfigElementText
                title="SMTP Port"
                value={localSectionConfig.smtp_port}
                setValue={(v: any) => setLocalConfigItem('error_email.smtp_port', v)}
                oldValue={centralSectionConfig.smtp_port}
                numeric
            />
            <configurationComponents.ConfigElementText
                title="SMTP Username"
                value={localSectionConfig.smtp_username}
                setValue={(v: string) => setLocalConfigItem('error_email.smtp_username', v)}
                oldValue={centralSectionConfig.smtp_username}
            />
            <configurationComponents.ConfigElementText
                title="SMTP Password"
                value={localSectionConfig.smtp_password}
                setValue={(v: string) => setLocalConfigItem('error_email.smtp_password', v)}
                oldValue={centralSectionConfig.smtp_password}
            />
            <configurationComponents.ConfigElementText
                title="Sender Address"
                value={localSectionConfig.sender_address}
                setValue={(v: string) => setLocalConfigItem('error_email.sender_address', v)}
                oldValue={centralSectionConfig.sender_address}
            />
            <configurationComponents.ConfigElementText
                title="Recipients"
                value={localSectionConfig.recipients}
                setValue={(v: string) => setLocalConfigItem('error_email.recipients', v)}
                oldValue={centralSectionConfig.recipients}
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>Add multiple recipient
                emails by splitting them with a comma.
            </div>
        </>
    );
}
