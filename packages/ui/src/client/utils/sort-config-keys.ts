import { sortBy } from 'lodash';

export default function sortConfigKeys(config: object) {
    return sortBy(Object.keys(config), key => {
        if (['tum_enclosure_is_present', 'is_present'].includes(key)) {
            key = '0' + key;
        }
        if (['ip'].includes(key)) {
            key = '1' + key;
        }
        return key;
    });
}
