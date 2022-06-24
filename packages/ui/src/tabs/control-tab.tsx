import { useSelector, useDispatch } from 'react-redux';
import { customTypes } from '../custom-types';
import { reduxUtils } from '../utils';

export default function ControlTab(props: { visible: boolean }) {
    const count = useSelector((state: customTypes.reduxState) => state.config.value);
    const dispatch = useDispatch();

    return (
        <div
            className={
                'w-full h-full relative ' + (props.visible ? 'flex ' : 'hidden ')
            }
        >
            <div className="flex-col-center">
                <div>count = {count}</div>
                <button onClick={() => dispatch(reduxUtils.configActions.increment())}>
                    Increment
                </button>
                <button onClick={() => dispatch(reduxUtils.configActions.decrement())}>
                    Decrement
                </button>
            </div>
        </div>
    );
}
