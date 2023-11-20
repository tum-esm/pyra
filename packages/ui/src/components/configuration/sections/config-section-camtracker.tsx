import toast from 'react-hot-toast';
import { configurationComponents } from '../..';
import { fetchUtils } from '../../../utils';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import useCommand from '../../../utils/fetch-utils/use-command';
import { Button } from '../../ui/button';

export default function ConfigSectionCamtracker() {
    const { centralConfig, localConfig, setLocalConfigItem, configIsDiffering } = useConfigStore();
    const { runPromisingCommand } = useCommand();

    const centralSectionConfig = centralConfig?.camtracker;
    const localSectionConfig = localConfig?.camtracker;

    function test() {
        if (configIsDiffering()) {
            toast.error('Please save your configuration before testing CamTracker connection.');
        } else {
            runPromisingCommand({
                command: fetchUtils.backend.testCamTracker,
                label: 'testing CamTracker connection',
                successLabel: 'successfully connected to CamTracker',
            });
        }
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <div>
                <Button onClick={test}>test CamTracker connection</Button>
            </div>
            <div className="flex-shrink-0 w-full mt-1 text-xs text-slate-500 flex-row-left gap-x-1">
                <p>
                    This test will start up CamTracker, check if it is running and close it again
                    using the values specified below.
                    <br />
                    <strong className="text-slate-600">This can take up to 90 seconds</strong>.
                </p>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Config Path"
                value={localSectionConfig.config_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.config_path', v)}
                oldValue={centralSectionConfig.config_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.executable_path', v)}
                oldValue={centralSectionConfig.executable_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementText
                title="Sun Intensity Path"
                value={localSectionConfig.sun_intensity_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.sun_intensity_path', v)}
                oldValue={centralSectionConfig.sun_intensity_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementText
                title="Learn Az Elev Path"
                value={localSectionConfig.learn_az_elev_path}
                setValue={(v: string) => setLocalConfigItem('camtracker.learn_az_elev_path', v)}
                oldValue={centralSectionConfig.learn_az_elev_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Motor Offset Threshold"
                value={localSectionConfig.motor_offset_threshold}
                setValue={(v: number) => setLocalConfigItem('camtracker.motor_offset_threshold', v)}
                oldValue={centralSectionConfig.motor_offset_threshold}
                postfix="degree(s)"
                numeric
            />
            <configurationComponents.ConfigElementNote>
                CamTracker will log its current motor position into the "learn_az_elev" file. When
                CamTracker has already been running and its motor position is more than this
                threshold away from the theoretical sun position, Pyra will restart CamTracker.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementBooleanToggle
                title="Restart if no logs"
                value={localSectionConfig.restart_if_logs_are_too_old}
                setValue={(v: boolean) =>
                    setLocalConfigItem('camtracker.restart_if_logs_are_too_old', v)
                }
                oldValue={centralSectionConfig.restart_if_logs_are_too_old}
            />
            <configurationComponents.ConfigElementBooleanToggle
                title="Restart if cover remains closed"
                value={localSectionConfig.restart_if_cover_remains_closed}
                setValue={(v: boolean) =>
                    setLocalConfigItem('camtracker.restart_if_cover_remains_closed', v)
                }
                oldValue={centralSectionConfig.restart_if_cover_remains_closed}
            />
            <configurationComponents.ConfigElementNote>
                If CamTracker does not log its motor position or the enclosure cover remains closed
                for more than 5 minutes after startup, and these options are enabled, Pyra will
                restart CamTracker. These states indicate that CamTracker is stuck at initialization
                - usually fixed by a restart.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
