import { configureStore } from '@reduxjs/toolkit';
import configReducer from './config-slice';

export default configureStore({
    reducer: {
        config: configReducer.reducer,
    },
});
