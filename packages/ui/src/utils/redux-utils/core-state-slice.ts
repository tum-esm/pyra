import { createSlice } from '@reduxjs/toolkit';
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
            state.content = action.payload;
        },
        setLoading: (state: customTypes.reduxStateCoreState, action: { payload: boolean }) => {
            state.loading = action.payload;
        },
    },
});

export default coreStateSlice;
