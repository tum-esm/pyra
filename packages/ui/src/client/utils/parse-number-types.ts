export default function parseNumberTypes(oldValue: any, newValue: any): any {
    if (typeof oldValue === 'string') {
        return newValue;
    }
    if (typeof oldValue === 'number') {
        const parsedNewValue = parseFloat(newValue);
        return `${parsedNewValue}` === `${newValue}`
            ? parsedNewValue
            : newValue;
    }
    if (typeof oldValue === 'object') {
        if (oldValue.length !== undefined) {
            return oldValue.map((v: any, i: number) =>
                parseNumberTypes(oldValue[i], newValue[i])
            );
        } else {
            const parsedNewValue: any = {};
            Object.keys(oldValue).forEach(key1 => {
                parsedNewValue[key1] = parseNumberTypes(
                    oldValue[key1],
                    newValue[key1]
                );
            });
            return parsedNewValue;
        }
    }
}
