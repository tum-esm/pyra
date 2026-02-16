import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionAEMETEnclosure() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.aemet_enclosure;
    const localSectionConfig = localConfig?.aemet_enclosure;

    function addDefault() {
        setLocalConfigItem('aemet_enclosure', {
            datalogger_ip: '10.10.0.5',
            datalogger_port: 80,
            datalogger_username: 'someone',
            datalogger_password: 'withapassword',

            em27_power_plug_ip: '10.10.0.2',
            em27_power_plug_port: 80,
            em27_power_plug_username: '',
            em27_power_plug_password: '',

            use_em27_power_plug: false,
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
                setValue={(v: string) => setLocalConfigItem('aemet_enclosure.datalogger_ip', v)}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.datalogger_ip : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                title="Datalogger Port"
                value={localSectionConfig.datalogger_port}
                setValue={(v: any) => setLocalConfigItem('aemet_enclosure.datalogger_port', v)}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.datalogger_port : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementText
                title="Datalogger Username"
                value={localSectionConfig.datalogger_username}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.datalogger_username', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.datalogger_username
                        : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                title="Datalogger Password"
                value={localSectionConfig.datalogger_password}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.datalogger_password', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.datalogger_password
                        : 'null'
                }
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="EM27 Power Plug IP"
                value={localSectionConfig.em27_power_plug_ip}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.em27_power_plug_ip', v)
                }
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.em27_power_plug_ip : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                title="EM27 Power Plug Port"
                value={localSectionConfig.em27_power_plug_port}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.em27_power_plug_port', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.em27_power_plug_port
                        : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementText
                title="EM27 Power Plug Username"
                value={localSectionConfig.em27_power_plug_username}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.em27_power_plug_username', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.em27_power_plug_username
                        : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                title="EM27 Power Plug Password"
                value={localSectionConfig.em27_power_plug_password}
                setValue={(v: string) =>
                    setLocalConfigItem('aemet_enclosure.em27_power_plug_password', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.em27_power_plug_password
                        : 'null'
                }
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Toggle EM27 Power"
                value={localSectionConfig.use_em27_power_plug}
                setValue={(v: boolean) =>
                    setLocalConfigItem('aemet_enclosure.use_em27_power_plug', v)
                }
                oldValue={centralSectionConfig?.use_em27_power_plug === true}
            />
            <configurationComponents.ConfigElementNote>
                I.e., turn off the power of the EM27/SUN whenever the sun elevation is below
                `config.general.min_sun_elevation`.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
