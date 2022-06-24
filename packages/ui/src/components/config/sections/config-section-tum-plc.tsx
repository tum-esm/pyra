import { customTypes } from '../../../custom-types';
import { configComponents, essentialComponents } from '../..';

export default function ConfigSectionTumPlc(props: {
    localConfig: customTypes.config;
    centralConfig: customTypes.config;
    addLocalUpdate(v: customTypes.partialConfig): void;
}) {
    const { localConfig, centralConfig, addLocalUpdate } = props;

    function addDefault() {
        addLocalUpdate({
            tum_plc: {
                min_power_elevation: 10.0,
                ip: '10.0.0.4',
                version: 1,
            },
        });
    }

    function setNull() {
        addLocalUpdate({
            tum_plc: null,
        });
    }

    if (localConfig.tum_plc === null) {
        return (
            <div className="relative space-y-2 text-sm flex-col-left">
                <div className="space-x-2 text-sm flex-row-left">
                    <span className="whitespace-nowrap">Not configured yet </span>
                    <essentialComponents.Button variant="slate" onClick={addDefault}>
                        set up now
                    </essentialComponents.Button>
                </div>
                <essentialComponents.PreviousValue
                    previousValue={
                        centralConfig.tum_plc !== null
                            ? JSON.stringify(centralConfig.tum_plc)
                                  .replace(/":/g, '": ')
                                  .replace(/,"/g, ', "')
                            : undefined
                    }
                />
                {centralConfig.tum_plc !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                )}
            </div>
        );
    }

    return (
        <>
            <essentialComponents.Button variant="slate" onClick={setNull}>
                remove configuration
            </essentialComponents.Button>
            <div className="w-full h-px my-6 bg-slate-300" />
            <configComponents.ConfigElementText
                key2="min_power_elevation"
                value={localConfig.tum_plc.min_power_elevation}
                setValue={(v: number) =>
                    addLocalUpdate({ tum_plc: { min_power_elevation: v } })
                }
                oldValue={
                    centralConfig.tum_plc !== null
                        ? centralConfig.tum_plc.min_power_elevation
                        : 'null'
                }
            />
            <configComponents.ConfigElementText
                key2="ip"
                value={localConfig.tum_plc.ip}
                setValue={(v: string) => addLocalUpdate({ tum_plc: { ip: v } })}
                oldValue={
                    centralConfig.tum_plc !== null ? centralConfig.tum_plc.ip : 'null'
                }
            />
            <configComponents.ConfigElementText
                key2="version"
                value={localConfig.tum_plc.version}
                setValue={(v: any) => addLocalUpdate({ tum_plc: { version: v } })}
                oldValue={
                    centralConfig.tum_plc !== null
                        ? centralConfig.tum_plc.version
                        : 'null'
                }
            />
        </>
    );
}
