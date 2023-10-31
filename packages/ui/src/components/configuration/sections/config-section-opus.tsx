import { configurationComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';

export default function ConfigSectionOpus() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.opus;
    const localSectionConfig = localConfig?.opus;

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="EM27 IP"
                value={localSectionConfig.em27_ip}
                setValue={(v: string) => setLocalConfigItem('opus.em27_ip', v)}
                oldValue={centralSectionConfig.em27_ip}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => setLocalConfigItem('opus.executable_path', v)}
                oldValue={centralSectionConfig.executable_path}
            />
            <configurationComponents.ConfigElementText
                title="Experiment Path"
                value={localSectionConfig.experiment_path}
                setValue={(v: string) => setLocalConfigItem('opus.experiment_path', v)}
                oldValue={centralSectionConfig.experiment_path}
            />
            <configurationComponents.ConfigElementText
                title="Macro Path"
                value={localSectionConfig.macro_path}
                setValue={(v: string) => setLocalConfigItem('opus.macro_path', v)}
                oldValue={centralSectionConfig.macro_path}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Username"
                value={localSectionConfig.username}
                setValue={(v: string) => setLocalConfigItem('opus.username', v)}
                oldValue={centralSectionConfig.username}
            />
            <configurationComponents.ConfigElementText
                title="Password"
                value={localSectionConfig.password}
                setValue={(v: string) => setLocalConfigItem('opus.password', v)}
                oldValue={centralSectionConfig.password}
            />
        </>
    );
}
