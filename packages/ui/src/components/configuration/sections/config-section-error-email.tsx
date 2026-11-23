import { Fragment } from 'react';
import toast from 'react-hot-toast';
import { configurationComponents } from '../..';
import { fetchUtils } from '../../../utils';
import useCommand from '../../../utils/fetch-utils/use-command';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionErrorEmail() {
    const { centralConfig, localConfig, setLocalConfigItem, configIsDiffering } = useConfigStore();
    const { runPromisingCommand } = useCommand();

    const centralSectionConfig = centralConfig?.error_email;
    const localSectionConfig = localConfig?.error_email;

    function test() {
        if (configIsDiffering()) {
            toast.error('Please save your configuration before sending the test email.');
        } else {
            runPromisingCommand({
                command: fetchUtils.backend.testEmail,
                label: 'sending test email',
                successLabel: 'successfully sent test email',
            });
        }
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <div>
                <Button onClick={test}>send test email</Button>
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
                Add multiple recipient emails by splitting them with a comma, i.e.
                `some.one@mail.com,another.one@mail.com`.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementNote>
                The account used to send the error emails. We recommend using a functional account
                from your institution, but you can also use public email providers like Gmail. We
                can add instructions for your instition here.
            </configurationComponents.ConfigElementNote>
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
            <configurationComponents.ConfigElementLine />
            <h3 className="text-sm font-semibold text-gray-700">Exception Email Patience</h3>
            <configurationComponents.ConfigElementNote>
                Set the delay in seconds before an unresolved exception triggers an email.
                Use -1 to send no emails for that exception. Values up to 86400 (one day) are allowed.
            </configurationComponents.ConfigElementNote>
            {[
                {
                    key: 'general',
                    visible: true,
                    rows: ([
                        ['cover-did-not-open', 'Cover Did Not Open'],
                        ['cover-did-not-close', 'Cover Did Not Close'],
                        ['storage-error', 'Storage Error'],
                        ['low-energy-error', 'Low Energy Error'],
                        ['pyra-core-crashed', 'Pyra Core Crashed'],
                        ['camtracker-configuration-error', 'CamTracker Configuration Error'],
                        ['helios-camera-error', 'Helios Camera Error'],
                        ['opus-connection-error', 'OPUS Connection Error'],
                        ['em27-connection-error', 'EM27 Connection Error'],
                        ['lock-timeout-error', 'Lock Timeout Error'],
                    ] as const).filter(([identifier]) =>
                        identifier !== 'helios-camera-error' || localConfig?.helios != null
                    ),
                },
                {
                    key: 'tum',
                    visible: localConfig?.tum_enclosure != null,
                    rows: [
                        ['tum-enclosure-plc-connection-error', 'TUM Enclosure PLC Connection Error'],
                        [
                            'tum-enclosure-rain-detected-cover-not-closed',
                            'TUM Enclosure Rain: Cover Not Closed',
                        ],
                        ['tum-enclosure-plc-reset-failed', 'TUM Enclosure PLC Reset Failed'],
                        ['tum-enclosure-plc-error', 'TUM Enclosure PLC Error'],
                    ] as const,
                },
                {
                    key: 'aemet',
                    visible: localConfig?.aemet_enclosure != null,
                    rows: [
                        ['aemet-enclosure-datalogger-error', 'AEMET Enclosure Datalogger Error'],
                    ] as const,
                },
            ]
                .filter((group) => group.visible)
                .map((group, index) => (
                    <Fragment key={group.key}>
                        {index > 0 && <configurationComponents.ConfigElementLine />}
                        {group.rows.map(([identifier, title]) => (
                            <configurationComponents.ConfigElementText
                                key={identifier}
                                title={title}
                                value={localSectionConfig.exception_patience[identifier]}
                                setValue={(v) =>
                                    setLocalConfigItem(
                                        `error_email.exception_patience.${identifier}`,
                                        v
                                    )
                                }
                                oldValue={centralSectionConfig.exception_patience[identifier]}
                                postfix="second(s)"
                                numeric
                            />
                        ))}
                    </Fragment>
                ))}
        </>
    );
}
