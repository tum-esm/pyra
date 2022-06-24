import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';
import logsSlice from './logs-slice';
import coreStateSlice from './core-state-slice';

export default configureStore({
    reducer: {
        config: configSlice.reducer,
        logs: logsSlice.reducer,
        coreState: coreStateSlice.reducer,
    },
});
