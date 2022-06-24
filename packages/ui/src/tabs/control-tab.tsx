import { reduxUtils } from '../utils';
import { essentialComponents } from '../components';

export default function ControlTab(props: { visible: boolean }) {
    const coreState = reduxUtils.useTypedSelector((s) => s.coreState.content);

    return (
        <div className={'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')}>
            {coreState === undefined && <essentialComponents.Spinner />}
            <div className="w-full break-all">
                {coreState !== undefined && JSON.stringify(coreState)}
            </div>
        </div>
    );
}
