import { customTypes } from '../../../custom-types';
import { configurationComponents, essentialComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionHelios() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.helios);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.helios);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    function addDefault() {
        update({
            helios: {
                camera_id: 0,
                evaluation_size: 15,
                seconds_per_interval: 6,
                measurement_threshold: 0.6,
                save_images: false,
            },
        });
    }

    function setNull() {
        update({
            helios: null,
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
            <div className="w-full h-px my-6 bg-gray-300" />
            <configurationComponents.ConfigElementText
                title="Camera ID"
                value={localSectionConfig.camera_id}
                setValue={(v: number) => update({ helios: { camera_id: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.camera_id : 'null'}
                numeric
            />
            <configurationComponents.ConfigElementText
                title="Seconds Per Interval"
                value={localSectionConfig.seconds_per_interval}
                setValue={(v: any) => update({ helios: { seconds_per_interval: v } })}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.seconds_per_interval
                        : 'null'
                }
                numeric
                postfix="second(s)"
            />
            <configurationComponents.ConfigElementText
                title="Evaluation Size"
                value={localSectionConfig.evaluation_size}
                setValue={(v: any) => update({ helios: { evaluation_size: v } })}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.evaluation_size : 'null'
                }
                numeric
                postfix="image(s)"
            />
            <configurationComponents.ConfigElementText
                title="Measurement Threshold"
                value={localSectionConfig.measurement_threshold}
                setValue={(v: any) => update({ helios: { measurement_threshold: v } })}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.measurement_threshold
                        : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementToggle
                title="Save Images"
                value={localSectionConfig.save_images}
                setValue={(v: boolean) => update({ helios: { save_images: v } })}
                oldValue={centralSectionConfig?.save_images === true}
            />
        </>
    );
}