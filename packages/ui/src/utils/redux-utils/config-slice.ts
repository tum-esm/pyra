import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
import { customTypes } from '../../custom-types';
import functionalUtils from '../functional-utils';

function configIsDiffering(state: customTypes.reduxStateConfig) {
    return (
        state !== undefined &&
        state !== undefined &&
        !functionalUtils.deepEqual(state.local, state.central)
    );
}

export const configSlice = createSlice({
    name: 'counter',
    initialState: {
        central: undefined,
        local: undefined,
        isDiffering: undefined,
    },
    reducers: {
        setConfigs: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.central = action.payload;
            state.local = action.payload;
            state.isDiffering = false;
        },
        setLocal: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.local = action.payload;
            state.isDiffering = configIsDiffering(state);
        },
        setLocalPartial: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.partialConfig }
        ) => {
            if (state.local !== undefined) {
                state.local = defaultsDeep(action.payload, JSON.parse(JSON.stringify(state.local)));
                state.isDiffering = configIsDiffering(state);
            }
        },
        resetLocal: (state: customTypes.reduxStateConfig) => {
            state.local = state.central;
        },
    },
});

export default configSlice;
