import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionHelios() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.helios;
    const localSectionConfig = localConfig?.helios;

    function addDefault() {
        setLocalConfigItem('helios', {
            camera_id: 0,
            evaluation_size: 15,
            seconds_per_interval: 6,
            edge_detection_threshold: 0.01,
            save_images: false,
        });
    }

    function setNull() {
        setLocalConfigItem('helios', null);
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }

    if (localSectionConfig === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <Button onClick={addDefault}>set up now</Button>
                {centralSectionConfig !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                )}
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
            <div>
                <Button onClick={setNull}>remove configuration</Button>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Camera ID"
                value={localSectionConfig.camera_id}
                setValue={(v: number) => setLocalConfigItem('helios.camera_id', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.camera_id : 'null'}
                numeric
            />
            <configurationComponents.ConfigElementNote>
                Normally is 0, sometimes 1 or 2. Helios will complain (see logs tab) if it cannot
                find the camera.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Seconds Per Interval"
                value={localSectionConfig.seconds_per_interval}
                setValue={(v: any) => setLocalConfigItem('helios.seconds_per_interval', v)}
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
                setValue={(v: any) => setLocalConfigItem('helios.evaluation_size', v)}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.evaluation_size : 'null'
                }
                numeric
                postfix="image(s)"
            />
            <configurationComponents.ConfigElementText
                title="Edge Detection Threshold"
                value={localSectionConfig.edge_detection_threshold}
                setValue={(v: any) => setLocalConfigItem('helios.edge_detection_threshold', v)}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.edge_detection_threshold
                        : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementNote>
                The lower this threshold, the more sensitive is Helios. More sensitive = more sun
                conditions are considered as "sunny enough to measure". A starting value of `0.01`
                is a good baseline. When the system should be measuring and is not, lower the
                threshold. When CamTracker is drifting a lot and is restarted frequently, increase
                the threshold.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementToggle
                title="Save Images"
                value={localSectionConfig.save_images}
                setValue={(v: boolean) => setLocalConfigItem('helios.save_images', v)}
                oldValue={centralSectionConfig?.save_images === true}
            />
        </>
    );
}
