import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
import { customTypes } from '../../custom-types';

export const coreStateSlice = createSlice({
    name: 'coreState',
    initialState: {
        content: undefined,
        loading: false,
    },
    reducers: {
        set: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.coreState }
        ) => {
            state.content = JSON.parse(JSON.stringify(action.payload));
            state.loading = false;
        },
        setPartial: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.partialCoreState }
        ) => {
            state.content = defaultsDeep(
                JSON.parse(JSON.stringify(action.payload)),
                JSON.parse(JSON.stringify(state.content))
            );
        },
        setLoading: (state: customTypes.reduxStateCoreState, action: { payload: boolean }) => {
            state.loading = action.payload;
        },
    },
});

export default coreStateSlice;
