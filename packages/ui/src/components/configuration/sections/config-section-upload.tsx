import { customTypes } from '../../../custom-types';
import { configurationComponents, essentialComponents } from '../..';
import { reduxUtils } from '../../../utils';

export default function ConfigSectionUpload() {
    const centralSectionConfig = reduxUtils.useTypedSelector((s) => s.config.central?.upload);
    const localSectionConfig = reduxUtils.useTypedSelector((s) => s.config.local?.upload);
    const dispatch = reduxUtils.useTypedDispatch();

    const update = (c: customTypes.partialConfig) =>
        dispatch(reduxUtils.configActions.setLocalPartial(c));

    function addDefault() {
        update({
            upload: {
                is_active: false,
                host: '1.2.3.4',
                user: '...',
                password: '...',
                src_directory: '...',
                dst_directory: '...',
                remove_src_after_upload: false,
            },
        });
    }

    function setNull() {
        update({
            upload: null,
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
            <configurationComponents.ConfigElementToggle
                title="Is Active"
                value={localSectionConfig.is_active}
                setValue={(v: boolean) => update({ upload: { is_active: v } })}
                oldValue={centralSectionConfig?.is_active === true}
            />
            <configurationComponents.ConfigElementText
                title="Host"
                value={localSectionConfig.host}
                setValue={(v: string) => update({ upload: { host: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.host : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="User"
                value={localSectionConfig.user}
                setValue={(v: any) => update({ upload: { user: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.user : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="Password"
                value={localSectionConfig.password}
                setValue={(v: any) => update({ upload: { password: v } })}
                oldValue={centralSectionConfig !== null ? centralSectionConfig.password : 'null'}
            />
            <configurationComponents.ConfigElementText
                title="Source Directory Path"
                value={localSectionConfig.src_directory}
                setValue={(v: any) => update({ upload: { src_directory: v } })}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.src_directory : 'null'
                }
            />
            <configurationComponents.ConfigElementText
                title="Destination Directory Path (Server Side)"
                value={localSectionConfig.dst_directory}
                setValue={(v: any) => update({ upload: { dst_directory: v } })}
                oldValue={
                    centralSectionConfig !== null ? centralSectionConfig.dst_directory : 'null'
                }
            />
            <configurationComponents.ConfigElementToggle
                title="Remove Source After Upload"
                value={localSectionConfig.remove_src_after_upload}
                setValue={(v: boolean) => update({ upload: { remove_src_after_upload: v } })}
                oldValue={centralSectionConfig?.remove_src_after_upload === true}
            />
        </>
    );
}
