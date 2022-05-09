import { capitalize } from 'lodash';

export default function capitalizeConfigKey(key: string) {
    return key
        .split('_')
        .map(capitalize)
        .join(' ')
        .replace('Opus', 'OPUS')
        .replace('Plc', 'PLC')
        .replace('Ip', 'IP')
        .replace('Id', 'ID')
        .replace('Em27', 'EM27')
        .replace('Vbdsd', 'VBDSD')
        .replace('Tum', 'TUM')
        .replace('Camtracker', 'CamTracker')
        .replace('Measurement Triggers', 'Triggers');
}
