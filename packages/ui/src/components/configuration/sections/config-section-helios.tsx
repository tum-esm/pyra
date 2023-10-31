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
                <div className="space-x-2 text-sm flex-row-left">
                    <span className="whitespace-nowrap">Not configured yet</span>
                    <Button onClick={addDefault}>set up now</Button>
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
            <Button onClick={setNull}>remove configuration</Button>
            <div className="w-full h-px my-6 bg-gray-300" />
            <configurationComponents.ConfigElementText
                title="Camera ID"
                value={localSectionConfig.camera_id}
                setValue={(v: number) => setLocalConfigItem('helios.camera_id', v)}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.camera_id : 'null'}
                numeric
            />
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
            <configurationComponents.ConfigElementToggle
                title="Save Images"
                value={localSectionConfig.save_images}
                setValue={(v: boolean) => setLocalConfigItem('helios.save_images', v)}
                oldValue={centralSectionConfig?.save_images === true}
            />
        </>
    );
}
