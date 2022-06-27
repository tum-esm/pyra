import { customTypes } from '../../../custom-types';
import { configurationComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionMeasurementTriggers() {
    const centralSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.central?.measurement_triggers
    );
    const localSectionConfig = reduxUtils.useTypedSelector(
        (s) => s.config.local?.measurement_triggers
    );
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <configurationComponents.ConfigElementToggle
                key2="consider_time"
                value={localSectionConfig.consider_time}
                setValue={(v: boolean) => update({ measurement_triggers: { consider_time: v } })}
                oldValue={centralSectionConfig.consider_time}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementToggle
                key2="consider_sun_elevation"
                value={localSectionConfig.consider_sun_elevation}
                setValue={(v: boolean) =>
                    update({
                        measurement_triggers: { consider_sun_elevation: v },
                    })
                }
                oldValue={centralSectionConfig.consider_sun_elevation}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementToggle
                key2="consider_vbdsd"
                value={localSectionConfig.consider_vbdsd}
                setValue={(v: boolean) => update({ measurement_triggers: { consider_vbdsd: v } })}
                oldValue={centralSectionConfig.consider_vbdsd}
            />
            <div className="w-full h-px mb-6 -mt-2 bg-gray-300" />
            <configurationComponents.ConfigElementTime
                key2="start_time"
                value={localSectionConfig.start_time}
                setValue={(v) => update({ measurement_triggers: { start_time: v } })}
                oldValue={centralSectionConfig.start_time}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementTime
                key2="stop_time"
                value={localSectionConfig.stop_time}
                setValue={(v) => update({ measurement_triggers: { stop_time: v } })}
                oldValue={centralSectionConfig.stop_time}
            />
            <configurationComponents.ConfigElementText
                key2="min_sun_elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => update({ measurement_triggers: { min_sun_elevation: v } })}
                oldValue={centralSectionConfig.min_sun_elevation}
            />
            <div className="h-0 -mt-4" />
            <configurationComponents.ConfigElementText
                key2="max_sun_elevation"
                value={localSectionConfig.max_sun_elevation}
                setValue={(v: number) => update({ measurement_triggers: { max_sun_elevation: v } })}
                oldValue={centralSectionConfig.max_sun_elevation}
            />
        </>
    );
}
