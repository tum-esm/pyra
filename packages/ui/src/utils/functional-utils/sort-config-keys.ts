import { sortBy } from 'lodash';

// TODO: Not use this anymore

const priorities = [
    ['notify_recipients', 'type', 'manual_override'],
    ['ip', 'type'],
    ['sun_angle_start'],
    ['sun_angle_stop'],
];

export default function sortConfigKeys(config: object) {
    return sortBy(Object.keys(config), (key) => {
        priorities.forEach((p, i) => {
            if (p.includes(key)) {
                key = `${i}${key}`;
            }
        });
        return key;
    });
}
