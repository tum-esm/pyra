import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import './styles/index.css';
//import Main from './main';
import { reduxUtils } from './utils';
import { useEffect, useState } from 'react';
import io from 'socket.io-client';
import { drop, last } from 'lodash';

function SocketTester() {
    const [isConnected, setIsConnected] = useState(false);
    const [logLines, setLogLines] = useState<string[]>([]);
    const [socket, setSocket] = useState<any>(undefined);

    useEffect(() => {
        const newSocket = io(`http://localhost:5001`);
        setSocket(newSocket);
    }, []);

    useEffect(() => {
        if (socket !== undefined) {
            socket.on('connect', () => {
                setIsConnected(true);
            });

            socket.on('disconnect', () => {
                setIsConnected(false);
            });

            socket.on('new_log_lines', (newLogLines: string[]) => {
                if (logLines.length > 0) {
                    const currentLastLogTime: any = last(logLines)?.slice(0, 26);
                    const newLastLogTime: any = last(newLogLines)?.slice(0, 26);
                    if (newLastLogTime > currentLastLogTime) {
                        setLogLines(newLogLines);
                    }
                } else {
                    setLogLines(newLogLines);
                }
            });

            return () => {
                socket.off('connect');
                socket.off('disconnect');
                socket.off('new_log_lines');
            };
        }
    }, [socket, logLines]);

    return (
        <div className="w-screen h-screen p-2 flex-col-left gap-y-2">
            <div className="flex-row-left gap-x-3">
                <h1 className="font-semibold text-gray-900">Socket tester</h1>
                <div
                    className={
                        'rounded-md px-2 py-0.5 text-sm ' +
                        (isConnected ? 'text-green-800 bg-green-150 ' : 'text-red-800 bg-red-150 ')
                    }
                >
                    {isConnected ? 'connected' : 'not connected'}
                </div>
            </div>
            <div className="flex flex-col items-start justify-start flex-grow w-full p-2 overflow-scroll font-mono text-xs rounded-md bg-gray-75">
                {logLines.map((l) => (
                    <RenderedLogLine l={l} key={l} />
                ))}
            </div>
        </div>
    );
}

function RenderedLogLine(props: { l: string }) {
    if (props.l.includes('EXCEPTION')) {
        return <pre>{props.l}</pre>;
    }

    let l = props.l.replace(/\n/g, '');

    try {
        const timeSection = l.slice(11, 26);
        const sections = l.slice(29, undefined).split(' - ');
        const sourceSection = sections[0];
        const typeSection = sections[1];
        const messageSection = drop(sections, 2).join(' - ');

        let textStyle = 'text-gray-500 font-light';
        switch (typeSection) {
            case 'INFO':
                textStyle = 'text-gray-900 font-semibold';
                break;
            case 'WARNING':
            case 'EXCEPTION':
            case 'ERROR':
                textStyle = 'text-red-700 font-bold';
                break;
        }

        return (
            <div className={`flex-row-left gap-x-2 ${textStyle} whitespace-nowrap`}>
                <span>{timeSection}</span>
                <span>-</span>
                <span className="w-48">{sourceSection}</span>
                <span>-</span>
                <span className="w-16">{typeSection}</span>
                <span>-</span>
                <span>{messageSection}</span>
            </div>
        );
    } catch {
        return <></>;
    }
}

// @ts-ignore
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <Provider store={reduxUtils.store}>
        <SocketTester />
    </Provider>
);
