import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';
import coreStateSlice from './core-state-slice';

export default configureStore({
    reducer: {
        config: configSlice.reducer,
        coreState: coreStateSlice.reducer,
    },
});
