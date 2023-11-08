import { configurationComponents, essentialComponents } from '../..';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';
import { fetchUtils } from '../../../utils';
import { join } from '@tauri-apps/api/path';
import { convertFileSrc } from '@tauri-apps/api/tauri';
import { useEffect, useState } from 'react';
import moment from 'moment';

export default function ConfigSectionHelios() {
    const { centralConfig, localConfig, setLocalConfigItem } = useConfigStore();

    const centralSectionConfig = centralConfig?.helios;
    const localSectionConfig = localConfig?.helios;

    function addDefault() {
        setLocalConfigItem('helios', {
            camera_id: 0,
            evaluation_size: 15,
            seconds_per_interval: 6,
            min_seconds_between_state_changes: 180,
            edge_pixel_threshold: 0.01,
            edge_color_threshold: 40,
            target_pixel_brightness: 50,
            save_image_to_archive: false,
            save_current_images: false,
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
                    <div className="absolute -top-2.5 -left-1 w-1 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-blue-300" />
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
                title="Min. Seconds Between State Changes"
                value={localSectionConfig.min_seconds_between_state_changes}
                setValue={(v: any) =>
                    setLocalConfigItem('helios.min_seconds_between_state_changes', v)
                }
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.min_seconds_between_state_changes
                        : 'null'
                }
                numeric
                postfix="second(s)"
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementNote>
                In general: The lower these thresholds, the more sensitive is Helios. More sensitive
                = more sun conditions are considered as "sunny enough to measure". Hence, when the
                system should be measuring but is not, lower the thresholds. When CamTracker is
                drifting a lot and is restarted frequently, increase the thresholds.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementText
                title="Edge Pixel Threshold"
                value={localSectionConfig.edge_pixel_threshold}
                setValue={(v: any) => setLocalConfigItem('helios.edge_pixel_threshold', v)}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.edge_pixel_threshold
                        : 'null'
                }
                postfix="%"
                numeric
            />
            <configurationComponents.ConfigElementNote>
                How many pixels of the lense should be considered as "edge". A starting value of
                `0.01` is a good baseline, i.e. 1% of the lense is a hard edge.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementText
                title="Edge Color Threshold"
                value={localSectionConfig.edge_color_threshold}
                setValue={(v: any) => setLocalConfigItem('helios.edge_color_threshold', v)}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.edge_color_threshold
                        : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementNote>
                How hard does a shadow have to be to be considered as "edge". A starting value of
                `40` is a good baseline.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementText
                title="Target Pixel Brightness"
                value={localSectionConfig.target_pixel_brightness}
                setValue={(v: any) => setLocalConfigItem('helios.target_pixel_brightness', v)}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.target_pixel_brightness
                        : 'null'
                }
                numeric
            />
            <configurationComponents.ConfigElementNote>
                Every 5 minutes Helios takes an image with every availabe exposure time and picks
                the exposure time where the mean pixel brightness is closest to this value.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Save Images to Archive"
                value={localSectionConfig.save_images_to_archive}
                setValue={(v: boolean) => setLocalConfigItem('helios.save_images_to_archive', v)}
                oldValue={centralSectionConfig?.save_images_to_archive === true}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Save Current Images"
                value={localSectionConfig.save_current_image}
                setValue={(v: boolean) => setLocalConfigItem('helios.save_current_image', v)}
                oldValue={centralSectionConfig?.save_current_image === true}
            />
            {localSectionConfig.save_current_image && <HeliosImages />}
        </>
    );
}

function HeliosImages() {
    const [heliosImagePathRaw, setHeliosImagePathRaw] = useState<string | null>(null);
    const [heliosImagePathProcessed, setHeliosImagePathProcessed] = useState<string | null>(null);
    const [timestamp, setTimestamp] = useState<number>(moment().unix());

    async function updateHeliosImagePaths() {
        const projectDirPath = await fetchUtils.getProjectDirPath();
        setHeliosImagePathRaw(
            convertFileSrc(await join(projectDirPath, 'logs', 'current-helios-view-raw.jpg'))
        );
        setHeliosImagePathProcessed(
            convertFileSrc(await join(projectDirPath, 'logs', 'current-helios-view-processed.jpg'))
        );
    }

    useEffect(() => {
        updateHeliosImagePaths();

        const interval = setInterval(() => {
            setTimestamp(moment().unix());
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="grid grid-cols-2 gap-2 mt-2">
            <img
                src={(heliosImagePathRaw || '') + `?${timestamp}`}
                alt="Helios Image Raw"
                className="w-full overflow-hidden border-0 bg-slate-100"
            />
            <img
                src={(heliosImagePathProcessed || '') + `?${timestamp}`}
                alt="Helios Image Processed"
                className="w-full overflow-hidden border-0 bg-slate-100"
                style={{ outline: 'none' }}
            />
        </div>
    );
}
