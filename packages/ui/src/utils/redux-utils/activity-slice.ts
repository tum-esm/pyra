import { createSlice } from '@reduxjs/toolkit';
import { defaultsDeep } from 'lodash';
import { customTypes, reduxStateActivity } from '../../custom-types';
import functionalUtils from '../functional-utils';

function configIsDiffering(state: customTypes.reduxStateConfig) {
    return (
        state !== undefined &&
        state !== undefined &&
        !functionalUtils.deepEqual(state.local, state.central)
    );
}

export const activitySlice = createSlice({
    name: 'activity',
    initialState: {
        history: undefined,
    },
    reducers: {
        set: (
            state: customTypes.reduxStateActivity,
            action: { payload: customTypes.activityHistory }
        ) => {
            state.history = JSON.parse(JSON.stringify(action.payload));
        },
    },
});

export default activitySlice;
