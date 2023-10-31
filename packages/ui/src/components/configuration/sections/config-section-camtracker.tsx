import { configurationComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';

export default function ConfigSectionCamtracker() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.camtracker;
    const localSectionConfig = localConfig?.camtracker;

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="Config Path"
                value={localSectionConfig.config_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.config_path', v)}
                oldValue={centralSectionConfig.config_path}
            />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.executable_path', v)}
                oldValue={centralSectionConfig.executable_path}
            />
            <configurationComponents.ConfigElementText
                title="Sun Intensity Path"
                value={localSectionConfig.sun_intensity_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.sun_intensity_path', v)}
                oldValue={centralSectionConfig.sun_intensity_path}
            />
            <configurationComponents.ConfigElementText
                title='"learn_az_elev" Path'
                value={localSectionConfig.learn_az_elev_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.learn_az_elev_path', v)}
                oldValue={centralSectionConfig.learn_az_elev_path}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Motor Offset Threshold"
                value={localSectionConfig.motor_offset_threshold}
                setValue={(v: number) => setLocalConfigItem('camtracker.motor_offset_threshold', v)}
                oldValue={centralSectionConfig.motor_offset_threshold}
                postfix="degree(s)"
                numeric
            />
            <configurationComponents.ConfigElementNote>
                CamTracker will log its current motor position into the "learn_az_elev" file. When
                CamTracker has already been running and its motor position is more than this
                threshold away from the theoretical sun position, Pyra will restart CamTracker.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementToggle
                title="Restart if no logs"
                value={localSectionConfig.restart_if_logs_are_too_old}
                setValue={(v: boolean) =>
                    setLocalConfigItem('camtracker.restart_if_logs_are_too_old', v)
                }
                oldValue={centralSectionConfig.restart_if_logs_are_too_old}
            />
            <configurationComponents.ConfigElementNote>
                If CamTracker does not log its motor position for more than 5 minutes and this
                option is enabled, Pyra will restart CamTracker. This can indicate that CamTracker
                is stuck at initialization - usually fixed by a restart.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
