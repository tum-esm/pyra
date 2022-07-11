import { createSlice } from '@reduxjs/toolkit';
import { customTypes } from '../../custom-types';

export const coreProcessSlice = createSlice({
    name: 'coreProcess',
    initialState: {
        pid: undefined,
    },
    reducers: {
        set: (
            state: customTypes.reduxStateCoreProcess,
            action: { payload: customTypes.reduxStateCoreProcess }
        ) => {
            state.pid = action.payload.pid;
        },
    },
});

export default coreProcessSlice;
