import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionAEMETEnclosure() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.aemet_enclosure;
    const localSectionConfig = localConfig?.aemet_enclosure;

    function addDefault() {
        setLocalConfigItem('aemet_enclosure', {
            datalogger_ip: '10.0.0.4',
            datalogger_port: 8080,
            datalogger_username: 'someone',
            datalogger_password: 'withapassword',

            em27_power_plug_ip: '10.0.0.5',
            em27_power_plug_port: 8080,
            em27_power_plug_username: 'someone',
            em27_power_plug_password: 'withapassword',

            toggle_em27_power: false,
            controlled_by_user: false,
        });
    }

    function setNull() {
        setLocalConfigItem('aemet_enclosure', null);
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }

    if (localSectionConfig === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <Button onClick={addDefault}>set up now</Button>
                <essentialComponents.PreviousValue
                    previousValue={
                        centralSectionConfig !== null
                            ? JSON.stringify(centralSectionConfig)
                                  .replace(/":/g, '": ')
                                  .replace(/,"/g, ', "')
                            : undefined
                    }
                />
                {centralSectionConfig !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-blue-300" />
                )}
            </div>
        );
    }

    return (
        <>
            <div>
                <Button onClick={setNull}>remove configuration</Button>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Datalogger IP"
                value={localSectionConfig.datalogger_ip}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure_enclosure.datalogger_ip', v)
                }
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.datalogger_ip : 'null'
                }
            />
            />
        </>
    );
}
