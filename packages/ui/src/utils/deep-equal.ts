// I didn't find a built-in version yet. This code is from

import { reduce, uniq } from 'lodash';

// https://dmitripavlutin.com/how-to-compare-objects-in-javascript/#4-deep-equality
export default function deepEqual(a: any, b: any): boolean {
    const aIsObject = isObject(a);
    const bIsObject = isObject(b);

    if ((aIsObject && !bIsObject) || (!aIsObject && bIsObject)) {
        return false;
    }
    // now we can assume either both are objects or none

    if (!aIsObject) {
        if (a != b) {
            return false;
        }
        if ((a === '' && b === 0) || (b === '' && a === 0)) {
            return false;
        }
        return true;
    }

    // [true, false, ...] for each key in the objects
    const subequality = uniq([...Object.keys(a), ...Object.keys(b)]).map((k) => {
        return deepEqual(a[k], b[k]);
    });

    // checks if all are true
    return reduce(subequality, (prev, curr, i) => prev && curr, true);
}

function isObject(object: any) {
    return object != null && typeof object === 'object';
}
