import React, {ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {Form, useParams} from "react-router-dom";
import axios from "axios";

const ChatNew = () => {
    const {id} = useParams();
    const user_id = useMemo(() => Math.floor(Math.random() * 1000) + 1, []);
    let ws = new WebSocket(`ws://localhost:8000/ws/${id}/${user_id}`);

    function appendMessage(msg: any) {
        let messages = document.getElementById('messages') as HTMLElement
        let message = document.createElement('li')
        let content = document.createTextNode(msg)
        message.appendChild(content)
        messages.appendChild(message)
    }

    ws.onmessage = function(event) {
        appendMessage(event.data)
    };

    function sendMessage(e : FormEvent<HTMLFormElement>) {
        let input = document.getElementById("messageText") as HTMLInputElement
        let data = {
            "user_id": user_id,
            "message": input.value,
            "chat_id": id,
        };
        axios.post("http://localhost:8000/messages/", data).then();
        input.value = ''
        e.preventDefault()
    }

    const getMessages = async () => {
        let {data: messages} = await axios.get(`http://localhost:8000/messages/${id}`);
        for (const message of messages) {
            ws.send(JSON.stringify(message));
        }
    }

    return (
        <div className="flex flex-col items-center">
            <h1>Chat ID: {id}</h1>
            <h2>Your ID: <span>{user_id}</span></h2>

            <button className={"btn btn-secondary p-3 mt-3"} onClick={getMessages}>Получить историю сообщений</button>
            <form className={"mt-3"} action="" onSubmit={(e) => sendMessage(e)}>
                <input className="bg-green-300" type="text" id="messageText" autoComplete="off" />
                <button className={"btn btn-outline-success p-3 ml-2"}>Отправить</button>
            </form>
            <ul id='messages'> </ul>
        </div>

    );
};

export default ChatNew;
