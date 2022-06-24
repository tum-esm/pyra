import { customTypes } from '../../../custom-types';
import { configComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionGeneral() {
    const centralSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.central?.general
    );
    const localSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.local?.general
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
                key2="seconds_per_core_interval"
                value={localSectionConfig.seconds_per_core_interval}
                setValue={(v: number) =>
                    update({ general: { seconds_per_core_interval: v } })
                }
                oldValue={centralSectionConfig.seconds_per_core_interval}
            />
            <configComponents.ConfigElementToggle
                key2="test_mode"
                value={localSectionConfig.test_mode}
                setValue={(v: boolean) => update({ general: { test_mode: v } })}
                oldValue={centralSectionConfig.test_mode}
            />
            <configComponents.ConfigElementText
                key2="station_id"
                value={localSectionConfig.station_id}
                setValue={(v: string) => update({ general: { station_id: v } })}
                oldValue={centralSectionConfig.station_id}
            />
        </>
    );
}
