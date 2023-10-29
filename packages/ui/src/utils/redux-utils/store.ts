import { configureStore } from '@reduxjs/toolkit';
import configSlice from './config-slice';

export default configureStore({
    reducer: {
        config: configSlice.reducer,
    },
});
