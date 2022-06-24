import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';
import logsSlice from './logs-slice';

export default configureStore({
    reducer: {
        config: configSlice.reducer,
        logs: logsSlice.reducer,
    },
});
