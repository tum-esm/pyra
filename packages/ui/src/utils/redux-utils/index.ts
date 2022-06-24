import store from './store';
import configSlice from './config-slice';

export default {
    store,
    configActions: configSlice.actions,
};
