import { customTypes } from '../../../custom-types';
import { configurationComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionCamtracker() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.camtracker);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.camtracker);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="Config Path"
                value={localSectionConfig.config_path}
                setValue={(v: string) => update({ camtracker: { config_path: v } })}
                oldValue={centralSectionConfig.config_path}
            />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => update({ camtracker: { executable_path: v } })}
                oldValue={centralSectionConfig.executable_path}
            />
            <configurationComponents.ConfigElementText
                title="Sun Intensity Path"
                value={localSectionConfig.sun_intensity_path}
                setValue={(v: string) => update({ camtracker: { sun_intensity_path: v } })}
                oldValue={centralSectionConfig.sun_intensity_path}
            />
            <configurationComponents.ConfigElementText
                title='"learn_az_elev" Path'
                value={localSectionConfig.learn_az_elev_path}
                setValue={(v: string) => update({ camtracker: { learn_az_elev_path: v } })}
                oldValue={centralSectionConfig.learn_az_elev_path}
            />
            <configurationComponents.ConfigElementText
                title="Motor Offset Threshold"
                value={localSectionConfig.motor_offset_threshold}
                setValue={(v: number) => update({ camtracker: { motor_offset_threshold: v } })}
                oldValue={centralSectionConfig.motor_offset_threshold}
            />
        </>
    );
}
