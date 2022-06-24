import { configComponents } from '../..';
import { customTypes } from '../../../custom-types';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionOpus() {
    const centralSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.central?.opus
    );
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.opus);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configComponents.ConfigElementText
                key2="em27_ip"
                value={localSectionConfig.em27_ip}
                setValue={(v: string) => update({ opus: { em27_ip: v } })}
                oldValue={centralSectionConfig.em27_ip}
            />
            <configComponents.ConfigElementText
                key2="executable_path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => update({ opus: { executable_path: v } })}
                oldValue={centralSectionConfig.executable_path}
            />
            <configComponents.ConfigElementText
                key2="executable_parameter"
                value={localSectionConfig.executable_parameter}
                setValue={(v: string) => update({ opus: { executable_parameter: v } })}
                oldValue={centralSectionConfig.executable_parameter}
            />
            <configComponents.ConfigElementText
                key2="experiment_path"
                value={localSectionConfig.experiment_path}
                setValue={(v: string) => update({ opus: { experiment_path: v } })}
                oldValue={centralSectionConfig.experiment_path}
            />
            <configComponents.ConfigElementText
                key2="macro_path"
                value={localSectionConfig.macro_path}
                setValue={(v: string) => update({ opus: { macro_path: v } })}
                oldValue={centralSectionConfig.macro_path}
            />
        </>
    );
}
