import { createSlice } from '@reduxjs/toolkit';
import { customTypes } from '../../custom-types';

export const configSlice = createSlice({
    name: 'counter',
    initialState: {
        central: undefined,
        local: undefined,
    },
    reducers: {
        setCentral: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.central = action.payload;
        },
        setLocal: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.local = action.payload;
        },
        setConfigs: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.central = action.payload;
            state.local = action.payload;
        },
    },
});

export default configSlice;
