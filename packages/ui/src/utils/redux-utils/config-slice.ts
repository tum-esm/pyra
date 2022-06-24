import { createSlice } from '@reduxjs/toolkit';

type configType = {
    value: number;
};

export const configSlice = createSlice({
    name: 'counter',
    initialState: {
        value: 0,
    },
    reducers: {
        increment: (state: configType) => {
            // Redux Toolkit allows us to write "mutating" logic in reducers. It
            // doesn't actually mutate the state because it uses the Immer library,
            // which detects changes to a "draft state" and produces a brand new
            // immutable state based off those changes
            state.value += 1;
        },
        decrement: (state: configType) => {
            state.value -= 1;
        },
        incrementByAmount: (state: configType, action: { payload: number }) => {
            state.value += action.payload;
        },
    },
});

export default configSlice;
