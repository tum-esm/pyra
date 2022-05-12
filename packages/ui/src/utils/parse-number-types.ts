export default function parseNumberTypes(oldValue: any, newValue: any): any {
    if (typeof oldValue === 'string' || typeof oldValue === 'boolean') {
        return newValue;
    }
    if (typeof oldValue === 'number') {
        if (new RegExp('^\\d*(\\.\\d+)?$').test(newValue.toString())) {
            return parseFloat(newValue);
        } else {
            return newValue;
        }
    }
    if (typeof oldValue === 'object') {
        if (oldValue.length !== undefined) {
            return oldValue.map((v: any, i: number) =>
                parseNumberTypes(oldValue[i], newValue[i])
            );
        } else {
            const parsedNewValue: any = {};
            Object.keys(oldValue).forEach((key1) => {
                parsedNewValue[key1] = parseNumberTypes(oldValue[key1], newValue[key1]);
            });
            return parsedNewValue;
        }
    }
}
