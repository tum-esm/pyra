import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';
import logsSlice from './logs-slice';
import coreStateSlice from './core-state-slice';
import coreProcessSlice from './core-process-slice';
import activitySlice from './activity-slice';

export default configureStore({
    reducer: {
        activity: activitySlice.reducer,
        config: configSlice.reducer,
        logs: logsSlice.reducer,
        coreState: coreStateSlice.reducer,
        coreProcess: coreProcessSlice.reducer,
    },
});
