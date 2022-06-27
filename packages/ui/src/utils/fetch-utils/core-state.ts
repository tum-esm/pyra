import { customTypes } from '../../custom-types';
import backend from './backend';
import toast from 'react-hot-toast';
import { shell } from '@tauri-apps/api';
import reduxUtils from '../redux-utils';

async function coreState(
    dispatch: any,
    centralConfig: customTypes.config,
    pyraCoreIsRunning: boolean
) {
    dispatch(reduxUtils.coreStateActions.setLoading(true));
    let result: shell.ChildProcess;
    if (pyraCoreIsRunning && centralConfig.tum_plc?.controlled_by_user === false) {
        result = await backend.getState();
    } else {
        result = await backend.readFromPLC();
    }

    if (result.code !== 0) {
        console.error(`Could not fetch core state. processResult = ${JSON.stringify(result)}`);
        toast.error(`Could not fetch core state, please look in the console for details`);
    } else {
        try {
            const newCoreState = JSON.parse(result.stdout);
            dispatch(reduxUtils.coreStateActions.set(newCoreState));
        } catch {
            toast.error(`Could not fetch core state: ${result.stdout}`);
        }
    }
    dispatch(reduxUtils.coreStateActions.setLoading(false));
}

export default coreState;
