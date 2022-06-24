import { customTypes } from '../../../custom-types';
import { configComponents, essentialComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionVbdsd() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.vbdsd);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.vbdsd);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    function addDefault() {
        update({
            vbdsd: {
                camera_id: 0,
                evaluation_size: 15,
                seconds_per_interval: 6,
                measurement_threshold: 0.6,
                min_sun_elevation: 11.0,
            },
        });
    }

    function setNull() {
        update({
            vbdsd: null,
        });
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }

    if (localSectionConfig === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <div className="space-x-2 text-sm flex-row-left">
                    <span className="whitespace-nowrap">Not configured yet </span>
                    <essentialComponents.Button variant="white" onClick={addDefault}>
                        set up now
                    </essentialComponents.Button>
                    {centralSectionConfig !== null && (
                        <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                    )}
                </div>
                <essentialComponents.PreviousValue
                    previousValue={
                        centralSectionConfig !== null
                            ? JSON.stringify(centralSectionConfig)
                                  .replace(/":/g, '": ')
                                  .replace(/,"/g, ', "')
                            : undefined
                    }
                />
            </div>
        );
    }

    return (
        <>
            <essentialComponents.Button variant="white" onClick={setNull}>
                remove configuration
            </essentialComponents.Button>
            <div className="w-full h-px my-6 bg-slate-300" />
            <configComponents.ConfigElementText
                key2="camera_id"
                value={localSectionConfig.camera_id}
                setValue={(v: number) => update({ vbdsd: { camera_id: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.camera_id : 'null'}
                numeric
            />
            <configComponents.ConfigElementText
                key2="min_sun_elevation"
                value={localSectionConfig.min_sun_elevation}
                setValue={(v: number) => update({ vbdsd: { min_sun_elevation: v } })}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.min_sun_elevation : 'null'
                }
                numeric
            />
            <configComponents.ConfigElementText
                key2="seconds_per_interval"
                value={localSectionConfig.seconds_per_interval}
                setValue={(v: any) => update({ vbdsd: { seconds_per_interval: v } })}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.seconds_per_interval
                        : 'null'
                }
                numeric
            />
            <configComponents.ConfigElementText
                key2="evaluation_size"
                value={localSectionConfig.evaluation_size}
                setValue={(v: any) => update({ vbdsd: { evaluation_size: v } })}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.evaluation_size : 'null'
                }
                numeric
            />
            <configComponents.ConfigElementText
                key2="measurement_threshold"
                value={localSectionConfig.measurement_threshold}
                setValue={(v: any) => update({ vbdsd: { measurement_threshold: v } })}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.measurement_threshold
                        : 'null'
                }
                numeric
            />
        </>
    );
}
