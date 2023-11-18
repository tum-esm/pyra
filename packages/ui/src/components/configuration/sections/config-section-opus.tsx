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
                    This test will start up OPUS, run a macro, stop the macro and close OPUS again
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
            />
            <configurationComponents.ConfigElementText
                title="Experiment Path"
                value={localSectionConfig.experiment_path}
                setValue={(v: string) => setLocalConfigItem('opus.experiment_path', v)}
                oldValue={centralSectionConfig.experiment_path}
            />
            <configurationComponents.ConfigElementText
                title="Macro Path"
                value={localSectionConfig.macro_path}
                setValue={(v: string) => setLocalConfigItem('opus.macro_path', v)}
                oldValue={centralSectionConfig.macro_path}
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
        </>
    );
}
