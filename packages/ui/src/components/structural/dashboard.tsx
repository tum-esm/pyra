import { useEffect, useState } from 'react';
import { fetchUtils, reduxUtils } from '../../utils';
import { OverviewTab, AutomationTab, ConfigurationTab, LogTab, ControlTab } from '../../tabs';
import { essentialComponents, structuralComponents } from '../../components';
import { customTypes } from '../../custom-types';
import { diff } from 'deep-diff';
import { dialog } from '@tauri-apps/api';
import backend from '../../utils/fetch-utils/backend';
import toast from 'react-hot-toast';
import socketIOClient from 'socket.io-client';
import { last } from 'lodash';

const tabs = ['Overview', 'Automation', 'Configuration', 'Logs'];

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('Overview');
    const [socket, setSocket] = useState<any>(undefined);

    useEffect(() => {
        const newSocket = socketIOClient(`http://localhost:5001`);
        setSocket(newSocket);
    }, []);

    const dispatch = reduxUtils.useTypedDispatch();
    const logLines = reduxUtils.useTypedSelector((s) => s.logs.debugLines);

    useEffect(() => {
        if (socket !== undefined) {
            socket.on('connect', () => {
                console.log('socket is connected');
            });

            socket.on('disconnect', () => {
                console.log('socket is disconnected');
            });

            return () => {
                socket.off('connect');
                socket.off('disconnect');
            };
        }
    }, [socket]);

    useEffect(() => {
        if (socket !== undefined) {
            socket.on('new_log_lines', (newLogLines: string[]) => {
                if (logLines && logLines.length > 0) {
                    const currentLastLogTime: any = last(logLines)?.slice(0, 26);
                    const newLastLogTime: any = last(newLogLines)?.slice(0, 26);
                    if (newLastLogTime > currentLastLogTime) {
                        dispatch(reduxUtils.logsActions.set(newLogLines));
                    }
                } else {
                    dispatch(reduxUtils.logsActions.set(newLogLines));
                }
            });

            return () => {
                socket.off('new_log_lines');
            };
        }
    }, [socket, logLines]);

    useEffect(() => {
        if (socket !== undefined) {
            socket.on('new_core_state', (newCoreState: customTypes.coreState) => {
                dispatch(reduxUtils.coreStateActions.set(newCoreState));
            });

            return () => {
                socket.off('new_core_state');
            };
        }
    }, [socket]);

    /*
    const [rawConfigFileContent, _] = fetchUtils.useFileWatcher('config\\config.json', 10);

    // load config when config/config.json has changed
    // check, whether a reload is required
    useEffect(() => {
        if (rawConfigFileContent !== undefined) {
            const newCentralConfig: customTypes.config = JSON.parse(rawConfigFileContent);
            const diffsToCentral = diff(centralConfig, newCentralConfig);
            if (diffsToCentral === undefined) {
                return;
            }

            // measurement_decision.cli_decision_result is allowed to change
            // changing any other property from somewhere else than the UI requires
            // a reload of the window
            const reloadIsRequired =
                diffsToCentral.filter(
                    (d) =>
                        d.kind === 'E' &&
                        d.path?.join('.') !== 'measurement_decision.cli_decision_result'
                ).length > 0;

            if (reloadIsRequired) {
                dialog
                    .message('The config.json file has been modified. Reload required', 'PyRa 4 UI')
                    .then(() => window.location.reload());
            } else {
                dispatch(reduxUtils.configActions.setConfigsPartial(newCentralConfig));
            }
        }
    }, [rawConfigFileContent]);*/

    const centralConfig = reduxUtils.useTypedSelector((s) => s.config.central);
    const enclosureControlsIsVisible =
        centralConfig?.tum_plc !== null && centralConfig?.tum_plc !== undefined;

    return (
        <div className="flex flex-col items-stretch w-screen h-screen overflow-hidden">
            <structuralComponents.Header
                {...{
                    tabs: [...tabs, ...(enclosureControlsIsVisible ? ['PLC Controls'] : [])],
                    activeTab,
                    setActiveTab,
                }}
            />
            <main
                className={
                    'flex-grow w-full bg-gray-75 ' + 'h-[calc(200vh-1.5rem)] overflow-y-scroll'
                }
            >
                {[
                    ['Overview', <OverviewTab />],
                    ['Automation', <AutomationTab />],
                    ['Configuration', <ConfigurationTab />],
                    ['Logs', <LogTab />],
                ].map((t: any, i) => (
                    <div key={i} className={activeTab === t[0] ? '' : 'hidden'}>
                        {t[1]}
                    </div>
                ))}
                {enclosureControlsIsVisible && (
                    <div className={activeTab === 'PLC Controls' ? '' : 'hidden'}>
                        <ControlTab />
                    </div>
                )}
            </main>
            <structuralComponents.MessageQueue />
        </div>
    );
}
