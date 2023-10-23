import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';
import coreStateSlice from './core-state-slice';
import activitySlice from './activity-slice';

export default configureStore({
    reducer: {
        activity: activitySlice.reducer,
        config: configSlice.reducer,
        coreState: coreStateSlice.reducer,
    },
});
