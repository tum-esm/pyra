import backend from './backend';
import toast from 'react-hot-toast';
import reduxUtils from '../redux-utils';

async function logs(dispatch: any) {
    dispatch(reduxUtils.logsActions.setLoading(true));
    const result = await backend.readDebugLogs();
    if (result.code === 0) {
        const newLogLines = result.stdout.split('\n');
        dispatch(reduxUtils.logsActions.set(newLogLines));
    } else {
        console.error(`Could not fetch log files. processResult = ${JSON.stringify(result)}`);
        toast.error('Could not fetch log files - details in the console');
    }
    dispatch(reduxUtils.logsActions.setLoading(false));
}

export default logs;
