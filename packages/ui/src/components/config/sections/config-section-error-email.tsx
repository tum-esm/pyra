import { customTypes } from '../../../custom-types';
import { ICONS } from '../../../assets';
import { configComponents } from '../..';

export default function ConfigSectionErrorEmail(props: {
    localConfig: customTypes.config;
    centralConfig: any;
    addLocalUpdate(v: customTypes.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    return (
        <>
            <configComponents.ConfigElementToggle
                key2="notify_recipients"
                value={localConfig.error_email.notify_recipients}
                setValue={(v: boolean) =>
                    addLocalUpdate({ error_email: { notify_recipients: v } })
                }
                oldValue={centralConfig.error_email.notify_recipients}
            />
            <configComponents.ConfigElementText
                key2="sender_address"
                value={localConfig.error_email.sender_address}
                setValue={(v: string) =>
                    addLocalUpdate({ error_email: { sender_address: v } })
                }
                oldValue={centralConfig.error_email.sender_address}
            />
            <configComponents.ConfigElementText
                key2="sender_password"
                value={localConfig.error_email.sender_password}
                setValue={(v: string) =>
                    addLocalUpdate({ error_email: { sender_password: v } })
                }
                oldValue={centralConfig.error_email.sender_password}
            />
            <configComponents.ConfigElementText
                key2="recipients"
                value={localConfig.error_email.recipients}
                setValue={(v: string) =>
                    addLocalUpdate({ error_email: { recipients: v } })
                }
                oldValue={centralConfig.error_email.recipients}
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>Add multiple
                recipient emails by splitting them with a comma.
            </div>
        </>
    );
}
