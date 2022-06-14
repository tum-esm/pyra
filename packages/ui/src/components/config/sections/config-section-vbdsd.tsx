import TYPES from '../../../utils/types';
import ConfigElementText from '../rows/config-element-text';
import Button from '../../essential/button';
import PreviousValue from '../../essential/previous-value';

export default function ConfigSectionVbdsd(props: {
    localConfig: TYPES.config;
    centralConfig: TYPES.config;
    addLocalUpdate(v: TYPES.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    function addDefault() {
        addLocalUpdate({
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
        addLocalUpdate({
            vbdsd: null,
        });
    }

    if (localConfig.vbdsd === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <div className="space-x-2 text-sm flex-row-left">
                    <span className="whitespace-nowrap">Not configured yet </span>
                    <Button variant="slate" onClick={addDefault}>
                        set up now
                    </Button>
                    {centralConfig.vbdsd !== null && (
                        <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                    )}
                </div>
                <PreviousValue
                    previousValue={
                        centralConfig.vbdsd !== null
                            ? JSON.stringify(centralConfig.vbdsd)
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
            <Button variant="slate" onClick={setNull}>
                remove configuration
            </Button>
            <div className="w-full h-px my-6 bg-slate-300" />
            <ConfigElementText
                key2="camera_id"
                value={localConfig.vbdsd.camera_id}
                setValue={(v: number) => addLocalUpdate({ vbdsd: { camera_id: v } })}
                oldValue={
                    centralConfig.vbdsd !== null
                        ? centralConfig.vbdsd.camera_id
                        : 'null'
                }
                numeric
            />
            <ConfigElementText
                key2="min_sun_elevation"
                value={localConfig.vbdsd.min_sun_elevation}
                setValue={(v: number) =>
                    addLocalUpdate({ vbdsd: { min_sun_elevation: v } })
                }
                oldValue={
                    centralConfig.vbdsd !== null
                        ? centralConfig.vbdsd.min_sun_elevation
                        : 'null'
                }
                numeric
            />
            <ConfigElementText
                key2="seconds_per_interval"
                value={localConfig.vbdsd.seconds_per_interval}
                setValue={(v: any) =>
                    addLocalUpdate({ vbdsd: { seconds_per_interval: v } })
                }
                oldValue={
                    centralConfig.vbdsd !== null
                        ? centralConfig.vbdsd.seconds_per_interval
                        : 'null'
                }
                numeric
            />
            <ConfigElementText
                key2="evaluation_size"
                value={localConfig.vbdsd.evaluation_size}
                setValue={(v: any) => addLocalUpdate({ vbdsd: { evaluation_size: v } })}
                oldValue={
                    centralConfig.vbdsd !== null
                        ? centralConfig.vbdsd.evaluation_size
                        : 'null'
                }
                numeric
            />
            <ConfigElementText
                key2="measurement_threshold"
                value={localConfig.vbdsd.measurement_threshold}
                setValue={(v: any) =>
                    addLocalUpdate({ vbdsd: { measurement_threshold: v } })
                }
                oldValue={
                    centralConfig.vbdsd !== null
                        ? centralConfig.vbdsd.measurement_threshold
                        : 'null'
                }
                numeric
            />
        </>
    );
}
