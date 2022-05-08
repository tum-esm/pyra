import { range, sortBy } from 'lodash';

const priorities = [
    ['tum_enclosure_is_present', 'is_present', 'type', 'manual_override'],
    ['ip', 'type'],
    ['sun_angle_start'],
    ['sun_angle_stop'],
];

export default function sortConfigKeys(config: object) {
    return sortBy(Object.keys(config), key => {
        priorities.forEach((p, i) => {
            if (p.includes(key)) {
                key = `${i}${key}`;
            }
        });
        return key;
    });
}
