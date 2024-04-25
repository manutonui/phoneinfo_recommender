import { useState, useRef, useEffect } from "react";
import {io} from 'socket.io-client'

const Chatbox = () => {
    const ref = useRef(null);
    const [msg, setMsg] = useState('')
    const [msgs, setMsgs] = useState([])
    const [socket, setSocket] = useState(null);
    

    useEffect(() => {
        if ( socket != null ) {
            socket.on('delivermessage', (msgData) => {
                let jres = JSON.parse(msgData)
                console.log('[DELIVERY]:',jres)
                setMsgs(msgs => [...msgs, {data: jres, author: 'sys'}])
            })
        }
    }, [socket])

    useEffect(()=>{
        ref.current.scrollIntoView({ block: 'start' })
    }, [msgs])

    useEffect(()=>{
        let newSocket = null
        console.log(`ENV: ${process.env.REACT_APP_ENV}`)
        if (process.env.REACT_APP_ENV === 'PROD') { newSocket = io('https://litcode.xyz') }
        if (process.env.REACT_APP_ENV === 'DEV') { newSocket = io('http://localhost:5500') }
        // Establish socket connection when the component mounts
        setSocket(newSocket)
        console.log(`Socket: ${socket}`)
        return () => newSocket.disconnect()  // Clean up the socket connection when the component unmounts
    },[])

    
    const handleMsg = (e) => setMsg(e.target.value)

    const handleSend = () => {
        if (msg) {
            const msgData = {
                data: msg,
                author: 'user'
            }
            socket.emit('sendmessage', msgData)
            setMsgs([...msgs, msgData])
            setMsg('')
            console.log('[LOCAL UPDATE]', msgData)
        }
    }

    const handleEnter = (e) => { if (e.key === 'Enter') handleSend() }


    return (
        <div className="chatwindow">
            <div className="chatmsgs">
                {msgs.map( (ms, index) =>
                    (<span key={index} className={`msg ${ms.author === 'user' ? 'you':''}`}>
                        {
                            typeof ms.data === 'string' ? (<small>{ms.data}</small>)
                            : Array.isArray(ms.data) ? ( <span>{ ms.data.map((item, index) => (
                            <small key={index} className="one-smartphone">
                                {item.model}, {item.price}/-, {item.internal_memory}gb rom, {item.ram_capacity}gb ram, {item.battery_capacity}mah, {item.primary_camera_rear}MP, {item.screen_size} inch screen size, {item.resolution_width}x{item.resolution_height}px resolution, fast charging: {item.fast_charging_available}, external sd: {item.extended_memory_available} {item.model}<br/>
                            </small>
                            )) }</span>)
                            : (<p>Data is neither a string nor an array</p>)
                        }
                    </span>)
                )}
                <span ref={ref}></span>
            </div>
            <div className="input-group msgbox">
                <input onChange={handleMsg} className="form-control" placeholder='Message' value={msg} onKeyUp={handleEnter} />
                <button className="input-group-text" onClick={handleSend}><i className="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>
    );
}
 
export default Chatbox;