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
    name: 'config',
    initialState: {
        central: undefined,
        local: undefined,
        isDiffering: undefined,
        errorMessage: undefined,
    },
    reducers: {
        setConfigs: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.central = JSON.parse(JSON.stringify(action.payload));
            state.local = JSON.parse(JSON.stringify(action.payload));
            state.isDiffering = false;
        },
        setConfigsPartial: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.partialConfig }
        ) => {
            if (state.local !== undefined && state.central !== undefined) {
                state.central = defaultsDeep(
                    JSON.parse(JSON.stringify(action.payload)),
                    JSON.parse(JSON.stringify(state.central))
                );
                state.local = defaultsDeep(
                    JSON.parse(JSON.stringify(action.payload)),
                    JSON.parse(JSON.stringify(state.local))
                );
                state.isDiffering = configIsDiffering(state);
            }
        },
        setLocal: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.config | undefined }
        ) => {
            state.local = JSON.parse(JSON.stringify(action.payload));
            state.isDiffering = configIsDiffering(state);
        },
        setLocalPartial: (
            state: customTypes.reduxStateConfig,
            action: { payload: customTypes.partialConfig }
        ) => {
            if (state.local !== undefined) {
                state.local = defaultsDeep(
                    JSON.parse(JSON.stringify(action.payload)),
                    JSON.parse(JSON.stringify(state.local))
                );
                state.isDiffering = configIsDiffering(state);
                state.errorMessage = undefined;
            }
        },
        resetLocal: (state: customTypes.reduxStateConfig) => {
            state.local = JSON.parse(JSON.stringify(state.central));
            state.isDiffering = false;
        },
        setErrorMessage: (
            state: customTypes.reduxStateConfig,
            action: { payload: string | undefined }
        ) => {
            state.errorMessage = JSON.parse(JSON.stringify(action.payload));
        },
    },
});

export default configSlice;
