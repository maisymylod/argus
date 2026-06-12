import { useState } from "react";

import { useRunQueryMutation } from "../features/api";
import { pushMessage, setResult } from "../features/sessionSlice";
import { useAppDispatch, useAppSelector } from "../store";

const AOIS = [
  { value: "central_valley_ca", label: "Central Valley, CA" },
  { value: "amazon_rondonia", label: "Rondonia, Brazil" },
];

export default function ChatPanel() {
  const dispatch = useAppDispatch();
  const messages = useAppSelector((s) => s.session.messages);
  const [runQuery, { isLoading }] = useRunQueryMutation();

  const [aoi, setAoi] = useState(AOIS[0].value);
  const [before, setBefore] = useState("2023-06-15");
  const [after, setAfter] = useState("2023-09-15");
  const [text, setText] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const query = text.trim() || `Show vegetation change near ${aoi}`;
    dispatch(pushMessage({ role: "user", text: query }));
    setText("");
    try {
      const res = await runQuery({ aoi, before, after, query }).unwrap();
      dispatch(pushMessage({ role: "agent", text: res.answer, citations: res.citations }));
      dispatch(setResult(res));
    } catch {
      dispatch(pushMessage({ role: "agent", text: "Request failed. Is the gateway running?" }));
    }
  }

  return (
    <aside className="chat">
      <header className="chat-header">
        <h1>ARGUS</h1>
        <span>earth-observation agent</span>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <p className="hint">
            Ask about vegetation change for an area of interest. The agent fetches imagery,
            computes NDVI and change, runs a model, and grounds its answer in the knowledge base.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className="bubble">{m.text}</div>
            {m.citations && m.citations.length > 0 && (
              <ul className="citations">
                {m.citations.map((c, j) => (
                  <li key={j}>
                    <code>{c.source}</code> {c.detail}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {isLoading && <div className="msg agent"><div className="bubble">analyzing…</div></div>}
      </div>

      <form className="controls" onSubmit={submit}>
        <label>
          AOI
          <select value={aoi} onChange={(e) => setAoi(e.target.value)}>
            {AOIS.map((a) => (
              <option key={a.value} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
        </label>
        <div className="dates">
          <label>
            Before
            <input type="date" value={before} onChange={(e) => setBefore(e.target.value)} />
          </label>
          <label>
            After
            <input type="date" value={after} onChange={(e) => setAfter(e.target.value)} />
          </label>
        </div>
        <input
          className="query"
          placeholder="Ask a question…"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Running…" : "Send"}
        </button>
      </form>
    </aside>
  );
}
