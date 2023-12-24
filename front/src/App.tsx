import './App.css';
import axios from "axios";
import React, {ChangeEvent, useEffect, useRef, useState} from "react";
import internal from "stream";
import {useNavigate} from "react-router-dom";

let client_id = Math.floor(Math.random() * 1000) + 1;

async function getChats() {
    let {data: chats} = await axios.get("http://localhost:8000/chats");
    return chats;
}

function App() {
    const nav = useNavigate();
    const ref = useRef<any>();
    const [chatName, setChatName] = useState("")

    const getChat = (id: number) => {
        nav(`/chats/${id}`);
    };

    const [chats, setChats] = useState([])
    useEffect(() => {
        (async () => {
            const result = await getChats();
            setChats(() => result);
        })();
    }, []);

    useEffect(() => {
        console.log(chats);
    }, [chats]);

    const changeChatName = (e : ChangeEvent<HTMLInputElement>) => {
        const {value} = e.target;
        setChatName(() => value);
    }

    const createChat = async (e: any) => {
        let data = {
            "chat_name": chatName,
            "user_id": 0,
        };

        await axios.post("http://localhost:8000/chats/", data);
        ref.current.value = "";
    };

    const getDocumentation = async() => {
        nav("http://localhost:8000/docs")
    };

  return (
      <div className="flex flex-col items-center">
        <h1 className={"ml-2 mt-3"}>Здесь можно выбрать чат к которому подключиться</h1>
          <form className={"mt-3 ml-2"} onSubmit={(e) => createChat(e)}>
              <h3>Название чата: </h3>
              <input ref={ref} onChange={changeChatName} />
              <button className={"btn btn-outline-success ml-2"} type={"submit"}>Создать чат</button>
          </form>

          <h2 className={"ml-2 mt-3"}>Чаты: </h2>
          {
              chats.map(element => <button className={"btn btn-outline-primary ml-2"} key={element["id"]} onClick={() => getChat(element["id"])}>{element["chat_name"]}</button>)
          }
          <div className={"mt-3 ml-2"}>
              <a href={"http://localhost:8000/docs"} className={"btn btn-dark"}>Документация</a>
          </div>
      </div>
  );
}

export default App;
