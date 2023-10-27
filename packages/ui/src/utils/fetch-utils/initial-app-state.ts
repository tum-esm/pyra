import reduxUtils from '../redux-utils';
import backend from './backend';

/*
1. Check whether pyra-cli is available
2. Check whether config can be read
3. Possibly add config to reduxStore
4. Check whether pyra-core is running
5. Possibly add pyra-core PID to reduxStore
*/
async function initialAppState(
    dispatch: any,
    setBackendIntegrity: (
        value:
            | 'cli is missing'
            | 'config is invalid'
            | 'pyra-core is not running'
            | 'valid'
            | undefined
    ) => void,
    setPyraCorePid: (value: number | undefined) => void
): Promise<void> {
    setBackendIntegrity(undefined);
    console.debug('loading initial state ...');

    let result1 = undefined;
    try {
        result1 = await backend.pyraCliIsAvailable();
        if (!result1.stdout.includes('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...')) {
            throw '';
        }
    } catch {
        console.error(`Could not reach pyra-cli. processResult = ${JSON.stringify(result1)}`);
        setBackendIntegrity('cli is missing');
        return;
    }

    console.debug('found pyra-cli');

    let result2 = undefined;
    try {
        result2 = await backend.getConfig();
        const newConfig = JSON.parse(result2.stdout);
        dispatch(reduxUtils.configActions.setConfigs(newConfig));
    } catch {
        console.error(
            `Could not fetch config file. configProcessResult = ${JSON.stringify(result2)}`
        );
        setBackendIntegrity('config is invalid');
        return;
    }

    const result3 = await backend.checkPyraCoreState();
    if (!result3.stdout.includes('pyra-core is running with process ID')) {
        setPyraCorePid(-1);
        setBackendIntegrity('pyra-core is not running');
        return;
    }

    const pid = parseInt(result3.stdout.replace(/[^\d]/g, ''));
    setPyraCorePid(pid);
    setBackendIntegrity('valid');
}

export default initialAppState;
