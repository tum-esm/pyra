export function renderString(
    value: undefined | null | string | number,
    options?: { appendix: string }
) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return `${value}${options !== undefined ? options.appendix : ''}`;
    }
}

export function renderBoolean(
    value: undefined | null | boolean,
    options?: { trueLabel?: string; falseLabel?: string }
) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return value ? (options?.trueLabel ?? 'Yes') : (options?.falseLabel ?? 'No');
    }
}

export function renderColorfulBoolean(value: undefined | null | boolean) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return value ? (
            <span className="font-semibold text-red-700">yes</span>
        ) : (
            <span className="font-semibold text-green-700">no</span>
        );
    }
}

export function renderColorfulInteger(value: undefined | null | string | number) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return Number(value) == 0 ? (
            <span className="font-semibold text-green-700">0</span>
        ) : (
            <span className="font-semibold text-red-700">{Number(value).toFixed(0)}</span>
        );
    }
}

export function renderNumber(
    value: undefined | null | string | number,
    options?: { appendix: string }
) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return `${Number(value).toFixed(2)}${options !== undefined ? options.appendix : ''}`;
    }
}

export function renderInteger(
    value: undefined | null | string | number,
    options?: { appendix: string }
) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return `${Number(value).toFixed(0)}${options !== undefined ? options.appendix : ''}`;
    }
}

export function renderTimeObject(value: { hour: number; minute: number; second: number }) {
    const hourString = `${value.hour}`.padStart(2, '0');
    const minuteString = `${value.minute}`.padStart(2, '0');
    const secondString = `${value.second}`.padStart(2, '0');
    return `${hourString}:${minuteString}:${secondString}`;
}
