import { customTypes } from '../../custom-types';
import backend from './backend';
import toast from 'react-hot-toast';
import { diff } from 'deep-diff';
import { dialog } from '@tauri-apps/api';
import reduxUtils from '../redux-utils';

async function config(dispatch: any, centralConfig: customTypes.config) {
    const result = await backend.getConfig();
    if (result.code !== 0) {
        console.error(`Could not fetch core state. processResult = ${JSON.stringify(result)}`);
        toast.error(`Could not fetch core state, please look in the console for details`);
        return;
    }

    const newCentralConfig: customTypes.config = JSON.parse(result.stdout);
    const diffsToCentral = diff(centralConfig, newCentralConfig);
    console.log({ centralConfig, newCentralConfig, diffsToCentral });
    if (diffsToCentral === undefined) {
        return;
    }

    // measurement_decision.cli_decision_result is allowed to change
    // changing any other property from somewhere else than the UI requires
    // a reload of the window
    const reloadIsRequired =
        diffsToCentral.filter(
            (d) =>
                d.kind === 'E' && d.path?.join('.') !== 'measurement_decision.cli_decision_result'
        ).length > 0;

    if (reloadIsRequired) {
        dialog
            .message('The config.json file has been modified. Reload required', 'PyRa 4 UI')
            .then(() => window.location.reload());
    } else {
        dispatch(reduxUtils.configActions.setConfigsPartial(newCentralConfig));
    }
}

export default config;
