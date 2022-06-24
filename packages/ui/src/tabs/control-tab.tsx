import { reduxUtils } from '../utils';
import { essentialComponents } from '../components';

export default function ControlTab() {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.content);
    const plcIsControlledByUser = reduxUtils.useTypedSelector(
        (s) => s.config.central?.tum_plc?.controlled_by_user
    );

    if (coreState === undefined || plcIsControlledByUser === undefined) {
        return <></>;
    }
    return (
        <div className={'w-full relative px-6 py-4'}>
            {coreState === undefined && <essentialComponents.Spinner />}
            <div className="w-full break-all">{JSON.stringify(coreState)}</div>
        </div>
    );
}
