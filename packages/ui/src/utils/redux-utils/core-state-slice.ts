import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
import { customTypes } from '../../custom-types';

export const coreStateSlice = createSlice({
    name: 'coreState',
    initialState: null,
    reducers: {
        set: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.coreState }
        ) => {
            state = JSON.parse(JSON.stringify(action.payload));
        },
        setPartial: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.partialCoreState }
        ) => {
            if (state !== null) {
                state = defaultsDeep(
                    JSON.parse(JSON.stringify(action.payload)),
                    JSON.parse(JSON.stringify(state))
                );
            }
        },
    },
});

export default coreStateSlice;
