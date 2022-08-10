import { configurationComponents } from '../..';
import { customTypes } from '../../../custom-types';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionOpus() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.opus);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.opus);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="EM27 IP"
                value={localSectionConfig.em27_ip}
                setValue={(v: string) => update({ opus: { em27_ip: v } })}
                oldValue={centralSectionConfig.em27_ip}
            />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => update({ opus: { executable_path: v } })}
                oldValue={centralSectionConfig.executable_path}
            />
            <configurationComponents.ConfigElementText
                title="Experiment Path"
                value={localSectionConfig.experiment_path}
                setValue={(v: string) => update({ opus: { experiment_path: v } })}
                oldValue={centralSectionConfig.experiment_path}
            />
            <configurationComponents.ConfigElementText
                title="Macro Path"
                value={localSectionConfig.macro_path}
                setValue={(v: string) => update({ opus: { macro_path: v } })}
                oldValue={centralSectionConfig.macro_path}
            />
            <configurationComponents.ConfigElementText
                title="Username"
                value={localSectionConfig.username}
                setValue={(v: string) => update({ opus: { username: v } })}
                oldValue={centralSectionConfig.username}
            />
            <configurationComponents.ConfigElementText
                title="Password"
                value={localSectionConfig.password}
                setValue={(v: string) => update({ opus: { password: v } })}
                oldValue={centralSectionConfig.password}
            />
        </>
    );
}
