import store from './store';
import { useSelector, useDispatch, TypedUseSelectorHook } from 'react-redux';
import { customTypes } from '../../custom-types';
import configSlice from './config-slice';
import logsSlice from './logs-slice';

const useTypedSelector: TypedUseSelectorHook<customTypes.reduxState> = useSelector;
const useTypedDispatch: () => typeof store.dispatch = useDispatch;

export default {
    store,
    configActions: configSlice.actions,
    logsActions: logsSlice.actions,
    useTypedSelector,
    useTypedDispatch,
};
