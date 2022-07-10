import { customTypes } from '../../../custom-types';
import { configurationComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionGeneral() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.general);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.general);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementText
                title="Seconds Per Core Interval"
                value={localSectionConfig.seconds_per_core_interval}
                setValue={(v: number) => update({ general: { seconds_per_core_interval: v } })}
                oldValue={centralSectionConfig.seconds_per_core_interval}
            />
            <configurationComponents.ConfigElementToggle
                title="Test Mode"
                value={localSectionConfig.test_mode}
                setValue={(v: boolean) => update({ general: { test_mode: v } })}
                oldValue={centralSectionConfig.test_mode}
            />
            <configurationComponents.ConfigElementText
                title="Station ID"
                value={localSectionConfig.station_id}
                setValue={(v: string) => update({ general: { station_id: v } })}
                oldValue={centralSectionConfig.station_id}
            />
        </>
    );
}
