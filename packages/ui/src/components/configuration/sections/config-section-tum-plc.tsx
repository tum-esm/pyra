import { customTypes } from '../../../custom-types';
import { configurationComponents, essentialComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionTumPlc() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.tum_plc);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.tum_plc);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    function addDefault() {
        update({
            tum_plc: {
                min_power_elevation: 10.0,
                ip: '10.0.0.4',
                version: 1,
                controlled_by_user: false,
            },
        });
    }

    function setNull() {
        update({
            tum_plc: null,
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
                {centralSectionConfig !== null && (
                    <div className="absolute -top-2.5 -left-1 w-1.5 h-[calc(100%+0.625rem)] -translate-x-2.5 bg-yellow-400 rounded-sm" />
                )}
            </div>
        );
    }

    return (
        <>
            <essentialComponents.Button variant="white" onClick={setNull}>
                remove configuration
            </essentialComponents.Button>
            <div className="w-full h-px my-6 bg-slate-300" />
            <configurationComponents.ConfigElementText
                key2="min_power_elevation"
                value={localSectionConfig.min_power_elevation}
                setValue={(v: number) => update({ tum_plc: { min_power_elevation: v } })}
                oldValue={
                    centralSectionConfig !== null
                        ? centralSectionConfig.min_power_elevation
                        : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                key2="ip"
                value={localSectionConfig.ip}
                setValue={(v: string) => update({ tum_plc: { ip: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.ip : 'null'}
            />
            <configurationComponents.ConfigElementText
                key2="version"
                value={localSectionConfig.version}
                setValue={(v: any) => update({ tum_plc: { version: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.version : 'null'}
            />
        </>
    );
}