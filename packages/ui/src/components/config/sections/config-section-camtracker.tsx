import { customTypes } from '../../../custom-types';
import { configComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionCamtracker() {
    const centralSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.central?.camtracker
    );
    const localSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.local?.camtracker
    );
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configComponents.ConfigElementText
                key2="config_path"
                value={localSectionConfig.config_path}
                setValue={(v: string) => update({ camtracker: { config_path: v } })}
                oldValue={centralSectionConfig.config_path}
            />
            <configComponents.ConfigElementText
                key2="executable_path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => update({ camtracker: { executable_path: v } })}
                oldValue={centralSectionConfig.executable_path}
            />
            <configComponents.ConfigElementText
                key2="executable_path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => update({ camtracker: { executable_path: v } })}
                oldValue={centralSectionConfig.executable_path}
            />
            <configComponents.ConfigElementText
                key2="learn_az_elev_path"
                value={localSectionConfig.learn_az_elev_path}
                setValue={(v: string) =>
                    update({ camtracker: { learn_az_elev_path: v } })
                }
                oldValue={centralSectionConfig.learn_az_elev_path}
            />
            <configComponents.ConfigElementText
                key2="motor_offset_threshold"
                value={localSectionConfig.motor_offset_threshold}
                setValue={(v: number) =>
                    update({ camtracker: { motor_offset_threshold: v } })
                }
                oldValue={centralSectionConfig.motor_offset_threshold}
            />
        </>
    );
}
