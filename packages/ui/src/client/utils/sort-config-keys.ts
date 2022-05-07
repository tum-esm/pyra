import { sortBy } from 'lodash';

export default function sortConfigKeys(config: object) {
    return sortBy(Object.keys(config), key => {
        if (
            [
                'tum_enclosure_is_present',
                'is_present',
                'sensor_is_present',
                'type',
            ].includes(key)
        ) {
            key = '0' + key;
        }
        if (['ip', 'sun_angle_start'].includes(key)) {
            key = '1' + key;
        }
        if (['ip', 'sun_angle_stop'].includes(key)) {
            key = '2' + key;
        }
        return key;
    });
}
