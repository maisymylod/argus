import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { AgentResponse, Citation } from "./api";

export interface ChatMessage {
  role: "user" | "agent";
  text: string;
  citations?: Citation[];
}

interface SessionState {
  messages: ChatMessage[];
  result: AgentResponse | null;
}

const initialState: SessionState = {
  messages: [],
  result: null,
};

const sessionSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    pushMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },
    setResult(state, action: PayloadAction<AgentResponse>) {
      state.result = action.payload;
    },
  },
});

export const { pushMessage, setResult } = sessionSlice.actions;
export default sessionSlice.reducer;
