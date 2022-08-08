import { customTypes } from '../../../custom-types';
import { configurationComponents } from '../..';
import { reduxUtils } from '../../../utils';
import { ICONS } from '../../../assets';

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
                postfix="second(s)"
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
            <configurationComponents.ConfigElementText
                title="Min. Sun Elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => update({ general: { min_sun_elevation: v } })}
                oldValue={centralSectionConfig.min_sun_elevation}
                postfix="degree(s)"
            />
            <div className="w-full -mt-[1.125rem] pl-[12.5rem] text-xs text-blue-600 flex-row-left gap-x-1">
                <div className="w-4 h-4 text-blue-400">{ICONS.info}</div>The TUM PLC will start its
                operation one degree earlier. VBDSD will start at this angle.
            </div>
        </>
    );
}
