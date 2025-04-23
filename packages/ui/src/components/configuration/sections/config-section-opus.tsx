import { toast } from 'react-hot-toast';
import { configurationComponents } from '../..';
import { fetchUtils } from '../../../utils';
import useCommand from '../../../utils/fetch-utils/use-command';
import { useConfigStore } from '../../../utils/zustand-utils/config-zustand';
import { Button } from '../../ui/button';

export default function ConfigSectionOpus() {
    const { centralConfig, localConfig, setLocalConfigItem, configIsDiffering } = useConfigStore();
    const { runPromisingCommand } = useCommand();

    const centralSectionConfig = centralConfig?.opus;
    const localSectionConfig = localConfig?.opus;

    function test() {
        if (configIsDiffering()) {
            toast.error('Please save your configuration before testing OPUS connection.');
        } else {
            runPromisingCommand({
                command: fetchUtils.backend.testOpus,
                label: 'testing OPUS connection',
                successLabel: 'successfully connected to OPUS',
            });
        }
    }

    if (localSectionConfig === undefined || centralSectionConfig === undefined) {
        return <></>;
    }
    return (
        <>
            <div>
                <Button onClick={test}>test OPUS connection</Button>
            </div>
            <div className="flex-shrink-0 w-full mt-1 text-xs text-slate-500 flex-row-left gap-x-1">
                <p>
                    This test will start up OPUS, start a macro, stop the macro and close OPUS again
                    using the values specified below.
                    <br />
                    <strong className="text-slate-600">This can take up to 80 seconds</strong>.
                </p>
            </div>
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="EM27 IP"
                value={localSectionConfig.em27_ip}
                setValue={(v: string) => setLocalConfigItem('opus.em27_ip', v)}
                oldValue={centralSectionConfig.em27_ip}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Executable Path"
                value={localSectionConfig.executable_path}
                setValue={(v: string) => setLocalConfigItem('opus.executable_path', v)}
                oldValue={centralSectionConfig.executable_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementText
                title="Experiment Path"
                value={localSectionConfig.experiment_path}
                setValue={(v: string) => setLocalConfigItem('opus.experiment_path', v)}
                oldValue={centralSectionConfig.experiment_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementText
                title="Macro Path"
                value={localSectionConfig.macro_path}
                setValue={(v: string) => setLocalConfigItem('opus.macro_path', v)}
                oldValue={centralSectionConfig.macro_path}
                showSelector="file"
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementText
                title="Username"
                value={localSectionConfig.username}
                setValue={(v: string) => setLocalConfigItem('opus.username', v)}
                oldValue={centralSectionConfig.username}
            />
            <configurationComponents.ConfigElementText
                title="Password"
                value={localSectionConfig.password}
                setValue={(v: string) => setLocalConfigItem('opus.password', v)}
                oldValue={centralSectionConfig.password}
            />
            <configurationComponents.ConfigElementLine />
            <configurationComponents.ConfigElementNote>
                <p>
                    The Automatic Peak Positioning (APP) feature searches for OPUS files that have
                    been written to the local disk within the last 10 minutes and after the last
                    EM27/SUN powerup. It loads the interferograms from these OPUS files using the{' '}
                    <a
                        href="https://tum-esm-utils.netlify.app/api-reference#tum_esm_utilsopus"
                        className="inline font-semibold text-blue-500"
                    >
                        tum-esm-utils
                    </a>{' '}
                    Python library and calculates the peak position. If the peak position from the
                    last five readable OPUS files is identical and is less than 200 points off the
                    center, it will send this new peak position to the EM27/SUN.
                    <br />
                    Make sure to unload the ifg files frequently because the files loaded by OPUS
                    cannot be read by any other program.
                </p>
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementBooleanToggle
                title="Enable APP"
                value={localSectionConfig.automatic_peak_positioning}
                setValue={(v: boolean) => setLocalConfigItem(`opus.automatic_peak_positioning`, v)}
                oldValue={centralSectionConfig.automatic_peak_positioning}
            />
            <configurationComponents.ConfigElementText
                title="APP DC Min."
                value={localSectionConfig.automatic_peak_positioning_dcmin}
                setValue={(v: number) =>
                    setLocalConfigItem(`opus.automatic_peak_positioning_dcmin`, v)
                }
                oldValue={centralSectionConfig.automatic_peak_positioning_dcmin}
                numeric={true}
            />
            <configurationComponents.ConfigElementNote>
                Only interferograms that have an absolute DC mean value larger than this "APP DC
                Min." setting will be considered in the automatic peak positioning. This is an
                additional way to ensure that the peak position is not saved when the sun is not in
                the center of the receptor.
            </configurationComponents.ConfigElementNote>
            <configurationComponents.ConfigElementText
                title="APP Interferogram Path"
                value={localSectionConfig.interferogram_path}
                setValue={(v: string) => setLocalConfigItem('opus.interferogram_path', v)}
                oldValue={centralSectionConfig.interferogram_path}
                showSelector="directory"
            />
            <configurationComponents.ConfigElementNote>
                The Interferogram path should point to the directory containing today's
                interferograms files. You can use the wildcards '%Y', '%y', '%m', '%d' that will be
                replaced by the current date. Refer to the documentation for this 'automatic peak
                positioning'. Do not attach a '*' to the end: after replacing the date, it should
                point to exactly one directory.
            </configurationComponents.ConfigElementNote>
        </>
    );
}
