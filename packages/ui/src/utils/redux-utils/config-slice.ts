import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
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
        setLocalPartial: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.partialConfig }
        ) => {
            if (state.local !== undefined) {
                state.local = defaultsDeep(
                    action.payload,
                    JSON.parse(JSON.stringify(state.local))
                );
            }
        },
    },
});

export default configSlice;
