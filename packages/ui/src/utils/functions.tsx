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

export function renderBoolean(value: undefined | null | boolean) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return value ? 'Yes' : 'No';
    }
}

export function renderColorfulBoolean(value: undefined | null | boolean) {
    if (value === undefined || value === null) {
        return '-';
    } else {
        return value ? (
            <span className="text-red-700">Yes</span>
        ) : (
            <span className="text-green-700">No</span>
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
