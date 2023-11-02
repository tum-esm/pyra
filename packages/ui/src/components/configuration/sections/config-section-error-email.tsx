import { configurationComponents } from '../..';
import { fetchUtils } from '../../../utils';
import useCommand from '../../../utils/fetch-utils/use-command';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionErrorEmail() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();
    const { runPromisingCommand } = useCommand();

    const centralSectionConfig = centralConfig?.error_email;
    const localSectionConfig = localConfig?.error_email;

    function test() {
        runPromisingCommand({
            command: fetchUtils.backend.testEmail,
            label: 'sending test email',
            successLabel: 'successfully sent test email',
        });
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <div>
                <Button onClick={test}>Send Test Email</Button>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Send Error Emails"
                value={localSectionConfig.notify_recipients}
                setValue={(v: boolean) => setLocalConfigItem('error_email.notify_recipients', v)}
                oldValue={centralSectionConfig.notify_recipients}
            />
            <configurationComponents.ConfigElementLine />
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
            <configurationComponents.ConfigElementNote>
                Add multiple recipient emails by splitting them with a comma.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
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
            <configurationComponents.ConfigElementNote>
                For Gmail: Use "smtp.gmail.com" and "587".
                <br />
                For TUM: Use "postout.lrz.de" and "587".
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
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
            <configurationComponents.ConfigElementNote>
                For Gmail: Use the email address and the "App Password".
                <br />
                For TUM: Use the TUM ID and its password.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
