import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
import { customTypes } from '../../custom-types';

export const coreStateSlice = createSlice({
    name: 'coreState',
    initialState: {
        body: undefined,
    },
    reducers: {
        set: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.coreState }
        ) => {
            console.log('ELO');
            state.body = JSON.parse(JSON.stringify(action.payload));
        },
        setPartial: (
            state: customTypes.reduxStateCoreState,
            action: { payload: customTypes.partialCoreState }
        ) => {
            if (state.body !== undefined) {
                state.body = defaultsDeep(
                    JSON.parse(JSON.stringify(action.payload)),
                    JSON.parse(JSON.stringify(state.body))
                );
            } else {
                console.warn('Cannot coreState.setPartial with a null state');
            }
        },
    },
});

export default coreStateSlice;
