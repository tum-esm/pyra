import reduxUtils from '../redux-utils';
import backend from './backend';

/*
1. Check whether pyra-cli is available
2. Check whether config can be read
3. Possibly add config to reduxStore
*/
async function initialAppState(
    dispatch: any,
    setBackendIntegrity: (
        value: 'cli is missing' | 'config is invalid' | 'valid' | undefined
    ) => void
) {
    setBackendIntegrity(undefined);
    console.debug('loading initial state ...');

    const result1 = await backend.pyraCliIsAvailable();
    if (result1.stdout.includes('Usage: pyra-cli [OPTIONS] COMMAND [ARGS]...')) {
        console.debug('found pyra-cli');
    } else {
        console.error(`Could not reach pyra-cli. processResult = ${JSON.stringify(result1)}`);
        setBackendIntegrity('cli is missing');
        return;
    }

    const result2 = await backend.getConfig();
    try {
        const newConfig = JSON.parse(result2.stdout);
        dispatch(reduxUtils.configActions.setConfigs(newConfig));
        setBackendIntegrity('valid');
    } catch (e) {
        console.error(
            `Could not fetch config file. configProcessResult = ${JSON.stringify(result2)}`
        );
        setBackendIntegrity('config is invalid');
    }
}

export default initialAppState;
